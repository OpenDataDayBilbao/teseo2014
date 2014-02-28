from thesaurus import fullfil_thesaurus_db
from extract_names import extract_names
from cache import name_genders, university_locations, save_name_genders

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.teseo_model import Person, University
from model.dbconnection import dbconfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    # # Get names and surnames for people
    # print "Extracting names..."
    # extract_names()

    # # Fullfil people tables with gender
    # print "\n\nGetting genders..."
    # config = dbconfig
    # engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (config['user'], config['password'], config['host'], dbconfig['database']))
    # Session = sessionmaker(bind=engine)
    # session = Session()

    # for name, gender in name_genders.items():
    #     if gender and gender != 'None':
    #         for person in session.query(Person).filter(Person.first_name.startswith(name)):
    #             if person.first_name.encode('utf-8').split()[0] == name:
    #                 person.gender = gender
    #                 sys.stdout.write('\r %s - %s' % (person.name, gender))
    #                 sys.stdout.flush()
    #                 session.add(person)
    #                 session.commit()

    # # Generate the full hierarchy of unesco descriptors with codes
    # print "\n\nGenerating Unesco hierarchy..."
    # fullfil_thesaurus_db()

    # # Fulfill university tables with locations
    # print "\n\nGetting university locations..."
    # for uni, location in university_locations.items():
    #     uni_db = session.query(University).filter(University.name == uni).first()
    #     if uni_db:
    #         uni_db.location = location
    #         session.add(uni_db)
    #         session.commit()

    save_name_genders()
