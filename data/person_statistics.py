import MySQLdb

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.dbconnection import dbconfig

config = dbconfig

conn = MySQLdb.Connection(db=config['database'], host=config['host'], user=config['user'], passwd=config['password'])
cursor = conn.cursor()

cursor.execute('select count(distinct lower(name)) from person;')
total_persons = cursor.fetchall()[0][0]

regex = '^([[:space:]]*((de(l?|([[:space:]]+la))|san|la)[[:space:]]+)?[[:alpha:]-]+){1,2}[[:space:]]*,?[[:space:]]+[[:alpha:][:space:]\.-]+$'

cursor.execute("select count(distinct lower(name)) from person where lower(name) regexp '%s';" % regex)
persons_matched = cursor.fetchall()[0][0]

cursor.execute("select count(distinct lower(name)) from person where lower(name) not regexp '%s';" % regex)
missing_persons = cursor.fetchall()[0][0]

print "select distinct lower(name) from person where lower(name) not regexp '%s' limit 10;" % regex

print 'Matching: %.2f' % (persons_matched / float(total_persons) * 100)
print 'Missing: %.2f' % (missing_persons / float(total_persons) * 100)
