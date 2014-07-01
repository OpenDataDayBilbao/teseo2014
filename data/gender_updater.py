# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 17:03:30 2014

@author: aitor
"""
import gender
import json
import mysql.connector
import time
import gender_detection
import urllib2

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


def get_name_genders_igender():    
    name_pool = get_names()    
    genders = {}
    try:
        genders = json.load(open('genders_igender.json', 'r'))
        print 'Loaded %i genders' % (len(genders))
    except:
        pass
    
    for i, name in enumerate(name_pool):
        if not genders.has_key(name):
            if i % 50 == 0:
                print 'Processed', i, 'of', len (name_pool)
                json.dump(genders, open('genders_igender.json', 'w'))
                
            wait = 10  
            repeat = True
            while(repeat):
                try:
                    g, prob = gender_detection.get_gender(name)
                    genders[name] = g
                    repeat = False
                    wait = 10
                    time.sleep(0.1)                    
                except UnicodeEncodeError:
                    genders[name] = 'none'
                    repeat = False
                    wait = 10
                except:
                    repeat = True
                    json.dump(genders, open('genders_igender.json', 'w'))
                    print 'Waiting %i seconds' % (wait)
                    time.sleep(wait)
                    wait = wait * 6
        
 
    json.dump(genders, open('genders_igender.json', 'w'))
    
def get_name_genders_genderize():
    name_pool = get_names()

    chunk_size = 50
    total_chunks = len(name_pool)/chunk_size
    rest = len(name_pool)%chunk_size
    
    genders = {}

    for j in range(0, total_chunks):
        print '*******Chunk', j, '/', total_chunks
        names = []
        if j == total_chunks - 1:
            names = name_pool[j * chunk_size:total_chunks*chunk_size+rest]
        else:
            names = name_pool[j * chunk_size:(j+1)*chunk_size]


        gender_list = gender.getGenders(names) 
        
#        [
#          {"name":"peter","gender":"male","probability":"1.00","count":796},
#          {"name":"lois","gender":"female","probability":"0.94","count":70},
#          {"name":"stevie","gender":"male","probability":"0.63","count":39}
#        ]

        for g in gender_list:
            genders[g[0]] = g[1]

    json.dump(genders, open('genders_genderize.json', 'w'))
    
    
def merge_genders():
    genderize = json.load(open('genders_genderize.json', 'r'))
    igender = json.load(open('genders_igender.json', 'r'))
    
    different = []
    final = {}
    
    for name in igender:
        if igender[name] == 'none':
            try:
                final[name] = genderize[name].lower()
            except:
                final[name] = 'none'
        else:
            final[name] = igender[name].lower()
        try:
            if genderize[name].lower() != igender[name].lower() and igender[name] != 'none':
                different.append(name)
                final[name] = genderize[name].lower()
        except:
            pass
       
    return final
        

                
def update_genders():
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    
    genders = merge_genders()
    updated_names = []
    try:
        updated_names = json.load( open('updated_names.json', 'r'))
    except:
        pass
    
    for i, name in enumerate(genders):
        if i % 5 == 0:
            print '%i of %i' % (i, len(genders))
        if not name in updated_names:            
            query = "UPDATE person SET gender = '%s' WHERE first_name = '%s'" % (genders[name], name)
            cursor.execute(query)
            updated_names.append(name)
      
    try:
        os.remove('updated_names.json')  
    except:
        pass
    json.dump(updated_names, open('updated_names.json', 'w'))
    
    cursor.close()
    cnx.close()
            

    

print 'Updating genders...'
# The firs time do:
#get_name_genders_igender()
#get_name_genders_genderize()

update_genders()
print 'Done'