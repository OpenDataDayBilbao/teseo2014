# -*- coding: utf-8 -*-

from teseo_model import University

from sqlalchemy import create_engine #, func, and_
from sqlalchemy.orm import sessionmaker
from rdflib import ConjunctiveGraph, URIRef, RDF

import wikipedia

def get_dbpedia_uri(term, lang):
    """
    Get the corresponding DBpedia URI from a wikipedia term (taking in account the language of the term)
    """

    DBPEDIA_RESOURCE_URI = u'dbpedia.org/resource/'
    if lang == 'en':
        return u'http://%s%s' % (DBPEDIA_RESOURCE_URI, term)
    else:
        return u'http://%s.%s%s' % (lang, DBPEDIA_RESOURCE_URI, term)


def get_dbpedia_endpoint(lang):
    """
    Get the corresponding DBpedia SPARQL endpoint for a language
    """

    DBPEDIA_SPARQL_URL = u'dbpedia.org/sparql'
    if lang == 'en':
        return u'http://%s' % DBPEDIA_SPARQL_URL
    else:
        return u'http://%s.%s' % (lang, DBPEDIA_SPARQL_URL)


def search_dbpedia_trough_wikipedia(literal, lang='en'):
    """
    Search a literal in Wikipedia (taking in account the language of the literal) and return a list of related DBpedia resources
    """

    ret = []
    wikipedia.set_lang(lang)
    for term in wikipedia.search(str(literal)):
        #summary = wikipedia.summary(term, sentences=1)
        #imgs = wikipedia.page(term).images
        t = unicode(term).replace(' ', '_')
        ret.append(( term, get_dbpedia_uri(t, lang) ))
    return ret


def get_uri_types(uri, lang):
    g = ConjunctiveGraph('SPARQLStore')
    g.open(get_dbpedia_endpoint(lang))

    #print uri
    #print len(list( g.triples(( URIRef(uri), URIRef('http://dbpedia.org/ontology/country'), URIRef('http://es.dbpedia.org/resource/España') )) ))

    return [ str(typ) for typ in g.objects(URIRef(uri), RDF.type) ]

if __name__ == '__main__':
    import os, sys
    lib_path = os.path.abspath('../')
    sys.path.append(lib_path)
    from model.dbconnection import dbconfig

    config = dbconfig

    # Load from DB
    engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (config['user'], config['password'], config['host'], dbconfig['database']))

    Session = sessionmaker(bind=engine)
    session = Session()
    db_descriptors = []
    for uni in session.query(University).distinct(University.name):
        print uni.name.encode('utf-8').lower()
        found = False

        wikiresults = search_dbpedia_trough_wikipedia('universidad ' + uni.name.encode('utf-8').lower(), 'es')

        for result in wikiresults:
            uri = result[1]
            if 'http://dbpedia.org/ontology/University' in get_uri_types(uri, 'es'):
                found = True
                print uri
                break

        if not found:
            print '-'*30
            # print uni.name.encode('utf-8').lower()
            print wikiresults
            print '-'*30

