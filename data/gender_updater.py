# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 17:03:30 2014

@author: aitor
"""
import gender
import mysql.connector

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

base_dir = os.path.dirname(os.path.abspath(__file__))

def load_config():
    from model.dbconnection import dbconfig

    return dbconfig
    
def get_names(): 
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(first_name) FROM person")
    result = set()
    for name in cursor:
        first = name[0].split(' ')[0]
        result.add(first)
    cursor.close()
    cnx.close()

    return list(result)

def update_name_genders():
    name_pool = get_names()
    bad_names = []
    
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

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
            #print name, infered_gender, prob
            if infered_gender == 'None' or prob < 0.6:
                bad_names.append(name)
                
            query = "UPDATE person SET gender = '%s' WHERE first_name = '%s'" % (infered_gender, name)
            cursor.execute(query)
            
    
    cursor.close()
    cnx.close()

    

print 'Updating genders...'    
update_name_genders()
print 'Done'