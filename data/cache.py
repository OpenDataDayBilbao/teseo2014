# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 11:29:20 2014

@author: aitor
"""

# Own stuff imports
import gender

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)


# Library imports
import pickle
import difflib

base_dir = os.path.dirname(os.path.abspath(__file__))

def load_config():
    from model.dbconnection import dbconfig

    return dbconfig

#     config = {
#           'user': 'foo',
#           'password': 'bar',
#           'host': '127.0.0.1',
#           'database': 'teseo',
#         }
#
#     with open('pass.config', 'r') as inputfile:
#         for i, line in enumerate(inputfile):
#             if i == 0:
#                 config['user'] = line
#             elif i == 1:
#                 config['password'] = line
#             elif i > 1:
#                 break
#
#     return config

def get_university_ids():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor_unis = cnx.cursor()
    cursor_unis.execute("SELECT id, name FROM university")
    result = {}
    for university in cursor_unis:
        result[university[0]] = university[1]
    cursor_unis.close()

    with open( base_dir + "/cache/university_ids.p", "wb" ) as outfile:
        pickle.dump(result, outfile)

def load_university_ids():
    result = ""
    try:
        with open( base_dir + "/cache/university_ids.p", "rb" ) as infile:        
            result = pickle.load(infile)
    except:
        print "No cache file created: /cache/university_ids.p"
    return result


def save_thesis_ids():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT id FROM thesis")
    result = set()
    for thesis_id in cursor:
        result.add(thesis_id[0])
    cursor.close()
    result = list(result)

    with open( base_dir + "/cache/thesis_ids.p", "wb" ) as outfile:
        pickle.dump(result, outfile)

def load_thesis_ids():
    result = ""
    try:
        with open( base_dir + "/cache/thesis_ids.p", "rb" ) as infile:
                result = pickle.load(infile)
    except:
        print "No cache file created: /cache/thesis_ids.p"  
    return result

def save_descriptors():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT id, text FROM descriptor")
    result = {}
    for descriptor in cursor:
        result[descriptor[0]] = descriptor[1]
    cursor.close()

    with open( base_dir + "/cache/descriptors.p", "wb" ) as outfile:
        pickle.dump(result, outfile)

def load_descriptors():
    result = ""
    try:
        with open( base_dir + "/cache/descriptors.p", "rb" ) as infile:
                result = pickle.load(infile)
    except:
        print "No cache file created: /cache/descriptors.p"
    return result

def get_names():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(first_name) FROM person")
    result = set()
    for name in cursor:
        first = name[0].split(' ')[0]
        result.add(first)
    cursor.close()

    return list(result)

def save_name_genders():
    name_pool = get_names()

    result = {}
    bad_names = []

    chunk_size = 50
    total_chunks = len(name_pool)/chunk_size
    rest = len(name_pool)%chunk_size

    for j in range(0, total_chunks):
        print '*******Chunk', j, '/', total_chunks
        names = []
        if j == total_chunks - 1:
            names = name_pool[j * chunk_size:total_chunks*chunk_size+rest]
        else:
            names = name_pool[j * chunk_size:(j+1)*chunk_size]

        gender_list = gender.getGenders(names) #gender, prob, count

        for i, name in enumerate(names):
            infered_gender = gender_list[i][0]
            prob = float(gender_list[i][1])
            print name, infered_gender, prob
            if infered_gender == 'None' or prob < 0.6:
                bad_names.append(name)
            # else:
            #     cursor.execute('UPDATE person SET gender=%s WHERE')
            result[name] = infered_gender

    with open( base_dir + "/cache/genders.p", "wb" ) as outfile:
        pickle.dump(result, outfile)

    with open( base_dir + "/cache/badnames.p", "wb" ) as outfile:
        pickle.dump(bad_names, outfile)

    return bad_names

def load_genders():
    result = ""
    try:
        with open( base_dir + "/cache/genders.p", "rb" ) as infile:     
                result = pickle.load(infile)
    except:
        print "No cache file created: /cache/genders.p"
    return result

def get_complete_names():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(name) FROM person")
    result = []
    for name in cursor:
        result.append(name[0])
    cursor.close()
    return result

def check_similar_names():
    print 'Getting names'
    names = get_complete_names()
    print 'Total names:', len(names)
    # min similarity ratio between strings
    threshold_ratio = 0.8
    repeated = []
    count = 0.0

    for i, str_1 in enumerate(names):
        for j in range(i+1, len(names)):
            if count%10000 == 0:
                print 'Similar', count
            count+=1
            str_2 = names[j]

            if (difflib.SequenceMatcher(None, str_1, str_2).ratio() > threshold_ratio):
                print 'Similar', str_1, str_2
                repeated.append((str_1, str_2))

    with open( base_dir + "/cache/repeated.p", "wb" ) as outfile:
        pickle.dump(repeated, outfile)

    return repeated

def load_descriptor_codes():
    result = ""
    try:
        with open( base_dir + "/cache/descriptor_codes.p", "rb" ) as infile:        
            result = pickle.load(infile)
    except:
        print "No cache file created: /cache/descriptor_codes.p"
    return result

def load_codes_descriptor():
    result = ""
    try:
        with open( base_dir + "/cache/codes_descriptor.p", "rb" ) as infile:        
            result = pickle.load(infile)
    except:
        print "No cache file created: /cache/codes_descriptor.p"
    return result

def save_descriptor_codes():
    import mysql.connector
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT code, text FROM descriptor")

    descriptor = {}
    codes = {}    
    
    for desc in cursor:
        code = str(desc[0])
        text = desc[1]
        if len(code) < 6:
            print code
            print text
            
        descriptor[text] = code
        codes[code] = text
        
    cursor.close()
    with open( base_dir + "/cache/descriptor_codes.p", "wb" ) as outfile:
        pickle.dump(descriptor, outfile)
    with open( base_dir + "/cache/codes_descriptor.p", "wb" ) as outfile:
        pickle.dump(codes, outfile)

def regenerate_cache_files():
    print 'Creating universities id cache'
    get_university_ids()
    print 'Creating thesis id cache'
    save_thesis_ids()
    print 'Creating descriptor cache'
    save_descriptors()
    print 'Creating gender cache'
    save_name_genders()
    print 'Creating descriptor cache'
    save_descriptor_codes()



####################DATA#############################


thesis_ids = load_thesis_ids()

descriptors = load_descriptors()

name_genders = load_genders()

descriptor_codes = load_descriptor_codes()

codes_descriptor = load_codes_descriptor()

university_locations = {
    u'SANTIAGO DE COMPOSTELA':u'Galicia',
    u'AUT\xd3NOMA DE BARCELONA':u'Cataluña',
    u'UNIVERSITAT DE VAL\xc8NCIA (ESTUDI GENERAL)':u'Valencia',
    u'COMPLUTENSE DE MADRID':u'Madrid',
    u'OVIEDO':u'Asturias',
    u'AUT\xd3NOMA DE MADRID':u'Madrid',
    u'PA\xcdS VASCO/EUSKAL HERRIKO UNIBERTSITATEA':u'País Vasco',
    u'GRANADA':u'Andalucía',
    u'NACIONAL DE EDUCACI\xd3N A DISTANCIA':u'Madrid',
    u'BURGOS':u'Castilla y León',
    u'NAVARRA':u'Navarra',
    u'ALICANTE':u'Valencia',
    u'ROVIRA I VIRGILI':u'Cataluña',
    u'POLIT\xc9CNICA DE VALENCIA' :u'Valencia',
    u'SEVILLA' :u'Andalucía',
    u'EXTREMADURA' :u'Extremadura',
    u'ZARAGOZA' :u'Aragon',
    u'POMPEU FABRA' :u'Cataluña',
    u'POLIT\xc9CNICA DE MADRID' :u'Madrid',
    u'M\xc1LAGA' :u'Andalucía',
    u'POLIT\xc9CNICA DE CATALUNYA' :u'Cataluña',
    u'MIGUEL HERN\xc1NDEZ DE ELCHE' :u'Valencia',
    u'RIOJA' :u'La Rioja',
    u'CARLOS III DE MADRID' :u'Madrid',
    u'GIRONA' :u'Cataluña',
    u'BARCELONA' :u'Cataluña',
    u'VIGO' :u'Galicia',
    u'SALAMANCA' :u'Castilla y León',
    u'MURCIA' :u'Murcia',
    u'P\xdaBLICA DE NAVARRA' :u'Navarra',
    u'VALLADOLID' :u'Castilla y León',
    u'PALMAS DE GRAN CANARIA' :u'Islas Canarias',
    u'ALMER\xcdA' :u'Extremadura',
    u'LA LAGUNA' :u'Islas Canarias',
    u'LLEIDA' :u'Cataluña',
    u'C\xd3RDOBA' :u'Andalucía',
    u'C\xc1DIZ' :u'Andalucía',
    u'ILLES BALEARS' :u'Islas Baleares',
    u'ABAT OLIBA CEU' :u'Cataluña',
    u'ALCAL\xc1' :u'Madrid',
    u'DEUSTO' :u'País Vasco',
    u'EUROPEA DE MADRID' :u'Madrid',
    u'CANTABRIA' :u'Cantabria',
    u'JA\xc9N' :u'Andalucía',
    u'PONTIFICIA DE SALAMANCA' :u'Castilla y León',
    u'REY JUAN CARLOS' :u'Madrid',
    u'LE\xd3N' :u'Castilla y León',
    u'RAM\xd3N LLULL' :u'Cataluña',
    u'POLIT\xc9CNICA DE CARTAGENA' :u'Andalucía',
    u'PONTIFICIA COMILLAS' :u'Madrid',
    u'CASTILLA-LA MANCHA' :u'Castilla La Mancha',
    u'JAUME I DE CASTELL\xd3N' :u'Valencia',
    u'CAT\xd3LICA DE VALENCIA SAN VICENTE M\xc1RTIR' :u'Valencia',
    u'A CORU\xd1A' :u'Galicia',
    u'PABLO DE OLAVIDE' :u'Andalucía',
    u'SAN PABLO-CEU' :u'Madrid',
    u'HUELVA' :u'Andalucía',
    u'CARDENAL HERRERA-CEU' :u'Valencia',
    u'OBERTA DE CATALUNYA' :u'Cataluña',
    u'CAT\xd3LICA SAN ANTONIO' :u'Murcia',
    u'INTERNACIONAL DE CATALUNYA' :u'Cataluña',
    u'ANTONIO DE NEBRIJA' :u'Madrid',
    u'MONDRAG\xd3N UNIBERTSITATEA' :u'País Vasco',
    u'FRANCISCO DE VITORIA' :u'Madrid',
    u'CAMILO JOS\xc9 CELA' :u'Madrid',
    u'IE UNIVERSITY' :u'Madrid',
    u'INTERNACIONAL MEN\xc9NDEZ PELAYO' :u'Madrid',
    u'VIC' :u'Cataluña',
    u'INTERNACIONAL DE VALENCIA' :u'Valencia',
    u'ALFONSO X EL SABIO' :u'Madrid',
    u'A DISTANCIA DE MADRID' :u'Madrid',
    u'CAT\xd3LICA SANTA TERESA DE JES\xdaS DE \xc1VILA' :u'Castilla y León',
    u'SAN JORGE' :u'Aragón',
    u'INTERNACIONAL DE ANDALUC\xcdA' :u'Andalucía',
    u'EUROPEA MIGUEL DE CERVANTES' :u'Castilla y León',
    u'INTERNACIONAL DE LA RIOJA' :u'La Rioja',
    u'EUROPEA DE CANARIAS' :u'Islas Canarias',
    u'TECNOLOGÍA Y EMPRESA' :u'Madrid',
    u'INTERNACIONAL DE BURGOS' :u'Castilla y León',
}

university_ids = load_university_ids()


#this should be done the first time running this scripts
if __name__=='__main__':
    regenerate_cache_files()
