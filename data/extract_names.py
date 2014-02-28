import MySQLdb
import sys
import re

import os
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.dbconnection import dbconfig

config = dbconfig

conn = MySQLdb.Connection(db=config['database'], host=config['host'], user=config['user'], passwd=config['password'])
cursor = conn.cursor()

cursor.execute('select count(*) from person;')
total_persons = cursor.fetchall()[0][0]

sql_regex = '^([[:space:]]*((de(l?|([[:space:]]+la))|san|la)[[:space:]]+)?[[:alpha:]-]+){1,2}[[:space:]]*,?[[:space:]]+[[:alpha:][:space:]\.-]+$'
pattern = re.compile('^(\s*(?:(?:de(?:l?|(?:\s+la))|san|la)\s+)?[\w-]+)(\s*(?:(?:de(?:l?|(?:\s+la))|san|la)\s+)?[\w-]+)?\s*,?\s+([\w\s\.-]+)$', re.UNICODE)

cursor.execute("select id, lower(name) from person where lower(name) regexp '%s';" % sql_regex)
result = cursor.fetchall()
total = len(result)

missing = 0
for (index, (id, name)) in enumerate(result):
    match = re.search(pattern, name)
    if match:
        if match.group(1) is not None:
            first_surname = match.group(1).strip()
        else:
            first_surname = ''

        if match.group(2) is not None:
            second_surname = match.group(2).strip()
        else:
            second_surname = ''

        if match.group(3) is not None:
            first_name = match.group(3).strip()
        else:
            first_name = ''

        if first_surname is '' and second_surname is '' and first_name is '':
            missing = missing + 1

        cursor.execute("update person set first_name='%s', first_surname='%s', second_surname='%s' where id=%s;" % (first_name, first_surname, second_surname, id))

    sys.stdout.write('\r Processed %s of %s' % (index + 1, total))
    sys.stdout.flush()

sys.stdout.write('\n')

conn.commit()

print 'Process finished'
print 'Not matching: %.2f' % (missing / float(total) * 100)
print ''
print 'Total missing: %.2f' % ((total_persons - total)/ float(total_persons) * 100)

conn.close()
