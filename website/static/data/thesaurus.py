# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib

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
