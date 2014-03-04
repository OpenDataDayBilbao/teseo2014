from thesaurus import fullfil_thesaurus_db
from extract_names import extract_names
from cache import name_genders, university_locations, university_types

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.teseo_model import University
from model.dbconnection import dbconfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysql.connector

if __name__ == '__main__':
    # Get names and surnames for people
    print "Extracting names..."
    extract_names()

    # Fullfil people tables with gender
    print "\n\nGetting genders..."
    config = dbconfig
    engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (config['user'], config['password'], config['host'], dbconfig['database']))
    Session = sessionmaker(bind=engine)
    session = Session()

    cnx = mysql.connector.connect(**config)
    update_cnx = mysql.connector.connect(**config)

    cursor_pers = cnx.cursor()
    cursor_update_pers = update_cnx.cursor()

    cursor_pers.execute("SELECT id, first_name FROM person WHERE first_name <> '' ")
    for pers in cursor_pers:
        pers_id = pers[0]
        pers_name = pers[1].encode('utf-8').split()[0]
        if pers_name in name_genders and name_genders[pers_name] and name_genders[pers_name] != 'None':
            sys.stdout.write('%s - %s       \r' % (pers_id, name_genders[pers_name]))
            sys.stdout.flush()
            cursor_update_pers.execute("UPDATE person SET gender='%s' WHERE id=%s" % (name_genders[pers_name], pers_id))

    cursor_pers.close()
    cursor_update_pers.close()

    # Generate the full hierarchy of unesco descriptors with codes
    print "\n\nGenerating Unesco hierarchy..."
    fullfil_thesaurus_db()

    # Fulfill university tables with locations
    print "\n\nGetting university locations and type (private-public)..."
    for uni, location in university_locations.items():
        uni_db = session.query(University).filter(University.name == uni).first()
        if not uni_db:
            uni_db = University(name=uni)
        uni_db.location = location
        uni_db.private = university_types[uni] == 'private'
        session.add(uni_db)
        session.commit()
