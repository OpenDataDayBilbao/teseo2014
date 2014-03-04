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

config = load_config()


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
    total = len(distinct_titles)
    for i, title in enumerate(distinct_titles):
        if total%100 == 0:
            print 'Getting repeated ids:', (i/total)*100
        cursor.execute("SELECT id FROM thesis WHERE title= %s", (title,))
        name_ids = []
        for thesis_id in cursor:
            name_ids.append(thesis_id[0])
        if len(name_ids) > 1:
            repeated_ids.append(name_ids)
            
    cursor.close()
    return repeated_ids
    
#def merge_repeated_thesis():
#    cnx = mysql.connector.connect(**config)
#    cursor = cnx.cursor()
#    for id_group in repeated_ids:
#        
    
if __name__=='__main__':
    print 'Getting names'
    distinct_names = get_thesis_names()
    print 'Distinct names: ', len(distinct_names)
    repeated_ids = get_repeated_thesis_ids(distinct_names)
    print repeated_ids
            
    
    