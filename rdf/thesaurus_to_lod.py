# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.teseo_model import Descriptor
from model.dbconnection import dbconfig

from rdflib import Graph, URIRef

RESOURCE_PREFIX = 'http://apps.morelab.deusto.es/unesco/resource'

def get_unesco_lod_uri(descriptor):
    if not desc.parent:
        code = str(descriptor.code)[:2]
    else:
        code = str(descriptor.code)[:4] if str(descriptor.code)[4:] == '00' else str(descriptor.code)

    uri = 'http://skos.um.es/unesco6/%s' % code
    g = Graph()
    g.parse(uri + '/turtle', format='turtle')
    if len(g) > 0:
        related = []
        for rel in g.objects(URIRef(uri), URIRef('http://www.w3.org/2004/02/skos/core#related')):
            rel_code = rel.replace('http://skos.um.es/unesco6/', '')
            if len(rel_code) == 2:
                rel_code += '0000'
            elif len(rel_code) == 4:
                rel_code += '00'
            related.append(rel_code)
        return uri, related
    else:
        return None, None

if __name__ == '__main__':
    engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (dbconfig['user'], dbconfig['password'], dbconfig['host'], dbconfig['database']))

    Session = sessionmaker(bind=engine)
    session = Session()

    for desc in session.query(Descriptor).all():
        rdf = '''
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .

        <%(prefix)s/%(code)s> rdf:type skos:Concept ;
            skos:prefLabel  "%(label)s"@es ;
            skos:inScheme <%(prefix)s/scheme> ;
        '''
        if not desc.parent:
            rdf += 'skos:topConceptOf <%(prefix)s/scheme> ;\n'
        else:
            rdf += 'skos:broader <%(prefix)s/%(parent_code)s> ;\n' % {'prefix': RESOURCE_PREFIX, 'parent_code': desc.parent.code}
        for child in desc.children:
            rdf += 'skos:narrower <%(prefix)s/%(child_code)s> ;\n' % {'prefix': RESOURCE_PREFIX, 'child_code': child.code}

        unesco_uri, unesco_related = get_unesco_lod_uri(desc)

        if unesco_uri:
            rdf += 'owl:sameAs <%s> ;\n' % unesco_uri

            for rel_code in unesco_related:
                rdf += 'skos:related <%(prefix)s/%(rel_code)s> ;\n' % {'prefix': RESOURCE_PREFIX, 'rel_code': rel_code}

        rdf += 'skos:notation "%(code)s" .'
        rdf = rdf % { 'prefix': RESOURCE_PREFIX, 'code': str(desc.code), 'label': desc.text.encode('utf-8') }

        print rdf
