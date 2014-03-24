# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker

from slugify import slugify

from thesaurus_to_lod import RESOURCE_PREFIX as UNESCO_PREFIX
from universities_dbpedia import search_university_in_dbp

from sets import Set

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.teseo_model import Thesis, Person, University, Department
from model.dbconnection import dbconfig

from rdflib import Graph


RESOURCE_PREFIX = 'http://apps.morelab.deusto.es/teseo/resource'

panel_role_to_swrcfe = {
    'secretario': 'swrcfe:panelSecretaty',
    'vocal': 'swrcfe:panelVocal',
    'presidente': 'swrcfe:panelPresident',
    'ausente': 'swrcfe:panelAbsent',
}

advisor_role_to_swrcfe = {
    'Director': 'swrcfe:advisor',
    'Codirector': 'swrcfe:coadvisor'
}


def create_person_rdf(person):
    rdf = '''
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix swrcfe: <http://www.morelab.deusto.es/ontologies/swrcfe#> .
    @prefix dc: <http://purl.org/dc/elements/1.1/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    <%(prefix)s/person/%(name_slug)s> rdf:type foaf:Person ;
        foaf:name  "%(name)s" ;
    '''

    if person.gender:
        rdf += 'foaf:gender "%(gender)s" ; \n' % { 'gender': person.gender }

    rdf += 'rdfs:label "%(name)s" . \n'

    return rdf % { 'prefix': RESOURCE_PREFIX, 'name_slug': slugify(person.name), 'name': person.name }

def create_university_rdf(university, departments=[]):
    rdf = '''
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix swrcfe: <http://www.morelab.deusto.es/ontologies/swrcfe#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    <%(prefix)s/university/%(name_slug)s> rdf:type foaf:Person ;
        foaf:name  "%(name)s" ;
        foaf:based_near "%(place)s" ;
    '''

    dbp_uri = search_university_in_dbp(university.name)
    if dbp_uri:
        rdf += 'owl:sameAs <%(dbp_uri)s> ; \n' % { 'dbp_uri': dbp_uri }

    dept_rdfs = []
    for dept in departments:
        rdf += 'swrcfe:hasParts <%(prefix)s/university/%(university_slug)s/%(department_slug)s> ; \n' % \
            { 'prefix': RESOURCE_PREFIX, 'university_slug': slugify(university.name), 'department_slug': slugify(dept.name) }

        dept_rdfs.append(
            '''
            <%(prefix)s/university/%(university_slug)s/%(department_slug)s> rdf:type swrcfe:Department ;
                foaf:name "%(department_name)s" ;
                rdfs:label "%(department_name)s" .
            ''' % \
            { 'prefix': RESOURCE_PREFIX, 'university_slug': slugify(university.name), 'department_slug': slugify(dept.name), 'department_name': dept.name }
        )

    rdf += 'rdfs:label "%(name)s" . \n'

    rdf = rdf % { 'prefix': RESOURCE_PREFIX, 'name': university.name, 'name_slug': slugify(university.name), 'place': university.location }

    return rdf + '\n'.join(dept_rdfs)

def create_panel_rdf(evaluators):
    rdf = '<%(prefix)s/thesis/%(title_slug)s/evaluation> rdf:type swrcfe:EvaluationPanel ; \n'

    for evaluator in evaluators:
        rdf += '%(swrcfe_role)s <%(prefix)s/person/%(evaluator_slug)s> ; \n' % \
            { 'swrcfe_role': panel_role_to_swrcfe[evaluator.role], 'prefix': RESOURCE_PREFIX, 'evaluator_slug': slugify(evaluator.person.name) }

    rdf += 'swrcfe:evaluates <%(prefix)s/thesis/%(title_slug)s> . \n'
    return rdf

def sanitize_string(text):
    text = ' '.join(text.splitlines())
    text = text.replace('"', '\'')
    return text

def create_thesis_rdf(thesis):
    # BASIC INFO
    rdf = '''
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix swrcfe: <http://www.morelab.deusto.es/ontologies/swrcfe#> .
    @prefix dc: <http://purl.org/dc/elements/1.1/> .
    @prefix bibo: <http://purl.org/ontology/bibo/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    <%(prefix)s/thesis/%(title_slug)s> rdf:type swrcfe:PhDThesis ;
        dc:title  "%(title)s" ;
        rdfs:label "%(title)s" ;
    '''
    if thesis.summary:
        rdf += 'bibo:abstract "%(abstract)s" ;\n' % { 'abstract': sanitize_string(thesis.summary) }

    # ADVISORS
    rdf += 'dc:creator <%(prefix)s/person/%(person_slug)s> ;\n'

    for adv in thesis.advisors:
        rdf += '%(swrcfe_role)s <%(prefix)s/person/%(advisor_slug)s> ;\n' % { 'swrcfe_role': advisor_role_to_swrcfe[adv.role],'prefix': RESOURCE_PREFIX, 'advisor_slug': slugify(adv.person.name) }

    # UNIVERSITY & DEPARTMENT
    if thesis.university:
        rdf += 'swrcfe:university <%(prefix)s/university/%(university_slug)s> ;\n' % { 'prefix': RESOURCE_PREFIX, 'university_slug': slugify(thesis.university.name) }

    if thesis.department:
        rdf += 'swrcfe:department <%(prefix)s/university/%(university_slug)s/%(department_slug)s> ;\n' % { 'prefix': RESOURCE_PREFIX, 'university_slug': slugify(thesis.university.name), 'department_slug': slugify(thesis.department.name) }

    # EVALUATION PANEL
    if len(thesis.panel) > 0:
        rdf += 'swrcfe:evaluatedBy <%(prefix)s/thesis/%(title_slug)s/evaluation> ;\n'
        panel_rdf = create_panel_rdf( [evaluator for evaluator in thesis.panel] )

    #  UNESCO DESCRIPTORS
    for descriptor in thesis.descriptors:
        rdf += 'dc:subject <%(unesco_prefix)s/%(descriptor)s> ;\n' % {'unesco_prefix': UNESCO_PREFIX, 'descriptor': descriptor.code}

    rdf += 'dc:date "%(date)s" .\n\n'

    # APPEND PANEL RDF TO THE BOTTOM OF THE RDF STRING
    rdf += panel_rdf
    
    thesis.title = sanitize_string(thesis.title)

    # FILL THE GAPS
    try:
        rdf = rdf % { 'prefix': RESOURCE_PREFIX, 'title_slug': slugify(thesis.title), 'title': thesis.title, 'person_slug': slugify(thesis.author.name) ,'date': thesis.defense_date.isoformat() }
    except TypeError:
        print 'resource:', RESOURCE_PREFIX
        print 'Title slug:',slugify(thesis.title)
        print 'title', thesis.title
        print 'author slug', slugify(thesis.author.name)
        print 'date', thesis.defense_date.isoformat()

    return rdf


if __name__ == '__main__':
    engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (dbconfig['user'], dbconfig['password'], dbconfig['host'], dbconfig['database']))

    Session = sessionmaker(bind=engine)
    session = Session()

    g = Graph()

    theses = [ thesis for thesis in session.query(Thesis).all() ]
    len_theses = len(theses)
    for i, thesis in enumerate(theses):
        rdf = create_thesis_rdf(thesis)
        g.parse(data=rdf, format='turtle')
        sys.stdout.write('%d out of %d  \r' % (i, len_theses))
        sys.stdout.flush()

    people = [ person for person in session.query(Person).all() ]
    len_people = len(people)
    for i, person in enumerate(people):
        rdf = create_person_rdf(person)
        g.parse(data=rdf, format='turtle')
        sys.stdout.write('%d out of %d  \r' % (i, len_people))
        sys.stdout.flush()

    uni_depts = {}
    for uni_id, dept_id in session.query(distinct(Thesis.university_id), Thesis.department_id).all():
        if uni_id:
            if uni_id not in uni_depts:
                uni_depts[uni_id] = Set()
            if dept_id:
                uni_depts[uni_id].add(dept_id)

    universities = [ uni for uni in session.query(University).all() ]
    len_universities = len(universities)
    for i, uni in enumerate(universities):
        depts = []
        if uni.id in uni_depts:
            depts = [ session.query(Department).get(dept_id) for dept_id in uni_depts[int(uni.id)] ]
        rdf = create_university_rdf(uni, depts)
        g.parse(data=rdf, format='turtle')
        sys.stdout.write('%d out of %d  \r' % (i, len_universities))
        sys.stdout.flush()
		
	g.serialize(destination='teseo.n3', format='n3')















