# -*- coding: utf-8 -*-
"""
Created on Tue Mar 04 10:41:28 2014

@author: aitor
"""

import cache
import difflib
import json
import os
import mysql.connector


base_dir = os.path.dirname(os.path.abspath(__file__))

def load_config():
    from model.dbconnection import dbconfig

    return dbconfig
    
#checks for similar names
def check_similar_names():
    print 'Getting names'
    names = cache.get_complete_names()
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
    config = load_config()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT DISTINCT(title) FROM thesis")
    result = []
    for name in cursor:
        result.append(name[0])
    cursor.close()
    return result
    