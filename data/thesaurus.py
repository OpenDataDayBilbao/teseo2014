# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib

from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.thesaurus_model import Descriptor


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


def get_full_thesaurus(session, starting_code, ending_code, multiple, codes_in_order=False):
    code = starting_code
    while code < ending_code:
        code += multiple
        name = search_in_unesco_thesaurus(code=code)

        # If name is not None code exists, so let's find sub-codes -if any-
        if name:
            print code

            # Create the descriptor object
            desc = Descriptor(id=int(code), text=name)

            # Check if it has any parent, and if so, make the relationship
            parent = session.query(Descriptor).get(starting_code)
            if parent:
                desc.parent_code = parent.id

            # Save the descriptor in DB
            session.add(desc)
            session.commit()

            # Recursively call the function -if it can have any sub level-.
            # If what we add in each loop (multiple) is less than 1 we will get into a infinite loop checking the same code
            # So that's the way we stop the recursion and detect that there are no more sublevels
            if multiple/100 >= 1:
                get_full_thesaurus(session, code, code + multiple, multiple/100, True)

        # If we know that code numbers go in order (1000-1001-1002-1003-...), we can break the loop when we find any non-existing code
        elif codes_in_order:
            break


def get_thesaurus_codes_in_page(idGen, idMed, idEsp):
    cookies = cookielib.LWPCookieJar()
    handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)

    page_url = 'https://www.educacion.gob.es/teseo/listarMaterias.do'

    post_data = {
                'idGen': idGen,
                'idMed': idMed,
                'idEsp': idEsp,
                'texto': ''
                }

    post_data_encoded = urllib.urlencode(post_data)

    request_object = urllib2.Request(page_url, post_data_encoded)

    response = opener.open(request_object)

    soup = BeautifulSoup(response.read().decode('utf-8'))

    code_dict = {}

    for materia in soup.findAll('label', attrs = {'for': 'materias'}):
        try:
            scrapped_code = materia.a.next.split(' - ')[0][1:-1]
            scrapped_name = materia.a.next.split(' - ')[1]
            code_dict[scrapped_code] = scrapped_name
        except:
            print materia

    return code_dict


def get_full_thesaurus_from_lists(session):
    # Get parent codes (XX0000)
    parent_codes = get_thesaurus_codes_in_page('', '00', '00')
    for parent_code, parent_label in parent_codes.items():
        # Save in DB
        parent_desc = Descriptor(id=int(parent_code), text=parent_label)
        session.add(parent_desc)
        session.commit()

        # For each code, find subcodes (XXYY00)
        sub_codes = get_thesaurus_codes_in_page(parent_code[:2], '', '00')

        print parent_code
        for sub_code, sub_code_label in sub_codes.items():
            if sub_code != parent_code:
                print '\t' + sub_code

                # Save in DB
                sub_desc = Descriptor(id=int(sub_code), text=sub_code_label)
                sub_desc.parent = parent_desc
                session.add(sub_desc)
                session.commit()

                sub_sub_codes = get_thesaurus_codes_in_page(sub_code[:2], sub_code[2:4], '')
                for sub_sub_code, sub_sub_code_label in sub_sub_codes.items():
                    if sub_sub_code != sub_code:
                        print '\t\t' + sub_sub_code

                        # Save in DB
                        sub_sub_desc = Descriptor(id=int(sub_sub_code), text=sub_sub_code_label)
                        sub_sub_desc.parent = sub_desc
                        session.add(sub_sub_desc)
                        session.commit()


def fullfil_thesaurus_db():
    engine = create_engine('sqlite:///thesaurus.db')

    Base = declarative_base()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    get_full_thesaurus_from_lists(session)
