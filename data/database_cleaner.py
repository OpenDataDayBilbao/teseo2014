# -*- coding: utf-8 -*-
"""
Created on Tue Mar 04 10:41:28 2014

@author: aitor
"""

import difflib
import json
import mysql.connector

import os, sys

lib_path = os.path.abspath('../')
sys.path.append(lib_path)


base_dir = os.path.dirname(os.path.abspath(__file__))

def load_config():
    from model.dbconnection import dbconfig

    return dbconfig

#config = load_config()

config = dbconfig = {
    'user': 'teseo',
    'password': '',
    'host': 'thor.deusto.es',
    'database': 'teseo_clean',
}



def get_complete_names():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(name) FROM person")
    result = []
    for name in cursor:
        result.append(name[0])
    cursor.close()
    return result
    
#checks for similar names
def check_similar_names():
    print 'Getting names'
    names = get_complete_names()
    print 'Total names:', len(names)
    # min similarity ratio between strings
    threshold_ratio = 0.85
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

    with open( base_dir + "/cache/repeated_names.json", "wb" ) as outfile:
        json.dump(repeated, outfile)

    return repeated
    
def get_thesis_names():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(title) FROM thesis")
    result = []
    for name in cursor:
        result.append(name[0])
    cursor.close()
    return result
    

def get_repeated_thesis_ids(distinct_titles):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    repeated_ids = []
    total = float(len(distinct_titles))
    for i, title in enumerate(distinct_titles):
        if i%100 == 0:
            print 'Getting repeated ids:', (i/total)*100
        cursor.execute("SELECT id FROM thesis WHERE title= %s", (title,))
        name_ids = []
        for thesis_id in cursor:
            name_ids.append(thesis_id[0])
        if len(name_ids) > 1:
            print 'Repeated ids', name_ids
            repeated_ids.append(name_ids)
            
    cursor.close()
    
    with open( base_dir + "/cache/repeated_thesis_ids.json", "wb" ) as outfile:
        json.dump(repeated_ids, outfile)

    return repeated_ids
    
    
def check_repeated_thesis():
    print 'Getting names'
    distinct_names = get_thesis_names()
    print 'Distinct names: ', len(distinct_names)
    repeated_ids = get_repeated_thesis_ids(distinct_names)
    print repeated_ids
    
    
    
def delete_repeated_thesis():
    repeated_ids = json.load(open( base_dir + "/cache/repeated_thesis_ids.json", "rb" ))
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    deleted = 0
    for id_group in repeated_ids:
        id_group.sort()
        to_delete = id_group[0:len(id_group)-1]
        for thesis_id in to_delete:
            print 'Deleting:', thesis_id
            cursor.execute("DELETE FROM thesis WHERE id=" + str(thesis_id))            
            deleted +=1
   
    print 'Deleted tesis:', deleted   
    cursor.close()
    
def get_person_ids():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(id) FROM person")
    result = []
    for person_id in cursor:
        result.append(person_id[0])
    cursor.close()
    return result
    
def get_unused_person_ids(person_ids):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    unused_ids = []
    total = float(len(person_ids))
    
    for i, person_id in enumerate(person_ids):
        if i%100 == 0:
            print 'Getting unused persons:', (i/total)*100
            
        author = False
        advisor = False
        panel = False        
        
        cursor.execute("SELECT COUNT(id) FROM thesis WHERE author_id=%d", (person_id,))
        for total_thesis in cursor:
            try:
                if total_thesis[0] > 0:
                    author = True
            except:
                pass
                    
        cursor.execute("SELECT COUNT(thesis_id) FROM advisor WHERE person_id=%d", (person_id,))
        for total_thesis in cursor:
            try:
                if total_thesis[0] > 0:
                    advisor = True
            except:
                pass
                    
        cursor.execute("SELECT COUNT(thesis_id) FROM panel WHERE person_id=%d", (person_id,))
        for total_thesis in cursor:
            try:
                if total_thesis[0] > 0:
                    panel = True
            except:
                pass

        if not (author or advisor or panel):
            unused_ids.append(person_id)
        
    cursor.close()
    with open( base_dir + "/cache/unused_person_ids.json", "wb" ) as outfile:
        json.dump(unused_ids, outfile)

    return unused_ids
    
def check_unused_person_ids():
    print 'Getting all person ids'
    person_ids = get_person_ids()
    print 'Distinct ids: ', len(person_ids)
    unused_ids = get_unused_person_ids(person_ids)
    print unused_ids    
        
        
    
if __name__=='__main__':
    #check repeated thesis()
    #delete_repeated_thesis()
    
            
    
    