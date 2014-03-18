# -*- coding: utf-8 -*-

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

def search_university_in_dbp(name):
    if name == u'CÓRDOBA':
        # Otherwise it returns the one in Colombia (no way found to disambiguate)
        return u'http://es.dbpedia.org/resource/Universidad_de_Córdoba'
    elif name == u'PALMAS DE GRAN CANARIA':
        # Otherwise it returns the resource describing the library of the University, which is also typed as an University
        return u'http://es.dbpedia.org/resource/Universidad_de_Las_Palmas_de_Gran_Canaria'
    elif name == u'VIC':
        # It has no University type :-/
        return u'http://es.dbpedia.org/resource/Universidad_de_Vich'

    wikiresults = search_dbpedia_trough_wikipedia('universidad ' + name.encode('utf-8').lower(), 'es')

    for result in wikiresults:
        uri = result[1]
        if 'http://dbpedia.org/ontology/University' in get_uri_types(uri, 'es'):
            return uri

    return None

