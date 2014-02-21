# -*- coding: utf-8 -*-

from teseo_model import Descriptor #, Thesis

from sqlalchemy import create_engine #, func, and_
from sqlalchemy.orm import sessionmaker

import urllib
import urllib2
import cookielib
import pickle

from bs4 import BeautifulSoup

def find_unesco_thesaurus_code(descriptor):
    cookies = cookielib.LWPCookieJar()
    handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)

    page_url = 'https://www.educacion.gob.es/teseo/listarMaterias.do'

    post_data = {
                'idGen': '',
                'idMed': '',
                'idEsp': '',
                'texto': descriptor
                }

    post_data_encoded = urllib.urlencode(post_data)

    request_object = urllib2.Request(page_url, post_data_encoded)

    response = opener.open(request_object)

    soup = BeautifulSoup(response.read().decode('utf-8'))

    try:
        for materia in soup.find_all('label', attrs = {'for': 'materias'}):
            code = materia.a.next.split(' - ')[0][1:-1]
            name = materia.a.next.split(' - ')[1]
            if descriptor == name.encode('utf-8'):
                return code
        return None
    except:
        return None


if __name__ == '__main__':
    USER = ''
    PASS = ''
    DB_NAME = ''
    DB_HOST = ''

    try:
        # Load from pickle
        db_descriptors = pickle.load( open( 'cache/db_descriptors_no_slug.p', 'rb' ) )
    except:
        # Load from DB
        engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (USER, PASS, DB_HOST, DB_NAME))

        Session = sessionmaker(bind=engine)
        session = Session()
        db_descriptors = []
        for descriptor in session.query(Descriptor).distinct(Descriptor.text):
            db_descriptors.append(descriptor.text)
        pickle.dump( db_descriptors, open( 'cache/db_descriptors_no_slug.p', 'wb' ) )

    try:
        # Load from pickle
        descriptor_codes = pickle.load( open( 'cache/descriptor_codes.p', 'rb' ) )
    except:
        # Make posts to Teseo
        db_descriptors_len = str(len(db_descriptors))
        descriptor_codes = {}
        for i, descriptor in enumerate(db_descriptors):
            print '%s/%s - %s' % (str(i), db_descriptors_len, descriptor)
            unesco_code = find_unesco_thesaurus_code(descriptor.encode('utf-8'))
            print unesco_code
            descriptor_codes[descriptor] = unesco_code

        pickle.dump( descriptor_codes, open( 'cache/descriptor_codes.p', 'wb' ) )
