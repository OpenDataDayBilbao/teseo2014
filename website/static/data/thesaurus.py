# -*- coding: utf-8 -*-

from teseo_model import Descriptor #, Thesis

from sqlalchemy import create_engine #, func, and_
from sqlalchemy.orm import sessionmaker

import urllib
import urllib2
import cookielib
import pickle

from bs4 import BeautifulSoup

def search_in_unesco_thesaurus(code = None, descriptor = None):
    cookies = cookielib.LWPCookieJar()
    handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)

    page_url = 'https://www.educacion.gob.es/teseo/listarMaterias.do'

    idGen = ''
    idMed = ''
    idEsp = ''

    if code:
        code = str(code)
        if len(code) == 2:
            idGen = code
            idMed = '00'
            idEsp = '00'
        elif len(code) >= 4:
            idGen = code[:2]
            idMed = code[2:4]
            idEsp = '00' if len(code) == 4 else code[4:6]

    post_data = {
                'idGen': idGen,
                'idMed': idMed,
                'idEsp': idEsp,
                'texto': descriptor
                }

    post_data_encoded = urllib.urlencode(post_data)

    request_object = urllib2.Request(page_url, post_data_encoded)

    response = opener.open(request_object)

    soup = BeautifulSoup(response.read().decode('utf-8'))

    try:
        for materia in soup.find_all('label', attrs = {'for': 'materias'}):
            scrapped_code = materia.a.next.split(' - ')[0][1:-1]
            scrapped_name = materia.a.next.split(' - ')[1]
            if code:
                return scrapped_name
            else:
                if descriptor == scrapped_name.encode('utf-8'):
                    return scrapped_code
        return None
    except:
        return None


if __name__ == '__main__':
    USER = ''
    PASS = ''
    DB_NAME = ''
    DB_HOST = ''

    # Descriptors from DB
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

    # Dictionary with Descriptor - Unesco Code relationships
    try:
        # Load from pickle
        descriptor_codes = pickle.load( open( 'cache/descriptor_codes.p', 'rb' ) )
        code_descriptor = pickle.load( open( 'cache/code_descriptor.p', 'rb' ) )

        # Harcoded ones (not found in Teseo for character limitation or other problems)
        descriptor_codes['LUZ'] = '220911' if not descriptor_codes['LUZ'] else descriptor_codes['LUZ']
        pickle.dump( descriptor_codes, open( 'cache/descriptor_codes.p', 'wb' ) )

        code_descriptor['220911'] = 'LUZ'
        pickle.dump( code_descriptor, open( 'cache/code_descriptor.p', 'wb' ) )
    except:
        # Make posts to Teseo
        db_descriptors_len = str(len(db_descriptors))
        descriptor_codes = {}
        code_descriptor = {}
        for i, descriptor in enumerate(db_descriptors):
            print '%s/%s - %s' % (str(i), db_descriptors_len, descriptor)
            unesco_code = search_in_unesco_thesaurus(descriptor=descriptor.encode('utf-8'))
            descriptor_codes[descriptor] = unesco_code
            code_descriptor[unesco_code] = descriptor

        # Harcoded ones (not found in Teseo for character limitation or other problems)
        descriptor_codes['LUZ'] = '220911' if not descriptor_codes['LUZ'] else descriptor_codes['LUZ']
        code_descriptor['220911'] = 'LUZ'

        pickle.dump( descriptor_codes, open( 'cache/descriptor_codes.p', 'wb' ) )
        pickle.dump( code_descriptor, open( 'cache/code_descriptor.p', 'wb' ) )

    print len(descriptor_codes)
    print len(code_descriptor)
