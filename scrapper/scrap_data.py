# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)
from model.teseo_model import Thesis, Person, Descriptor, Department
from model.teseo_model import University, Advisor, PanelMember
from model.teseo_model import Base

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from datetime import datetime

import os
import gzip
import re
import sys

# engine = create_engine('mysql://%s:%s@localhost/%s?charset=utf8' % (USER, PASS, DB_NAME))

engine = create_engine('sqlite:///minotaur.db')

Session = sessionmaker(bind=engine)
session = Session()

def clean_str(source_str):
    return unicode(source_str).strip()

def extract_groups(source_str):
    matched = re.match(r'(.*?)\((.*?)\)', source_str, re.DOTALL)
    if matched is not None:
        return matched.groups()[0].strip(), matched.groups()[1].strip()
    return None, None

def scrap_data(file, id):
    soup = BeautifulSoup(file.read().decode('utf-8'))
    data_section = soup.find_all('div', attrs={'class': 'datos-resultado'})

    if len(data_section) != 1:
        raise Exception('Error getting data section element')

    thesis = Thesis(id)

    for field in data_section[0].find_all('li'):
        identifier = field.strong
        if identifier is not None:
            key = unicode(identifier.next).strip().replace(':', '')

            if key == u'Dirección':
                #multiple values
                for advisor in field.ul.find_all('li'):
                    name, role = extract_groups(clean_str(advisor.next))
                    advisor = Advisor(Person(name), role)
                    thesis.advisors.append(advisor)
            elif key == u'Tribunal':
                #multiple values
                for panel_member in field.ul.find_all('li'):
                    name, role = extract_groups(clean_str(panel_member.next))
                    panelMember = PanelMember(Person(name), role)
                    thesis.panel.append(panelMember)
            elif key == u'Descriptores':
                #multiple values
                for descriptor in field.ul.find_all('li'):
                    text = clean_str(descriptor.next)
                    descriptor = session.query(Descriptor).filter_by(text=text).first()
                    if descriptor is None:
                        descriptor = Descriptor(text)
                    thesis.descriptors.append(descriptor)
            elif key == u'Resumen':
                thesis.summary = clean_str(identifier.next_sibling.next_sibling.next)
            elif key == u'Universidad':
            	university_name = clean_str(identifier.next_sibling)
            	university = session.query(University).filter_by(name=university_name).first()
            	if university is None:
            		university = University(university_name)

            	thesis.university = university
            else:
                value = clean_str(identifier.next_sibling)
                if key == u'Título':
                    thesis.title = value
                elif key == u'Autor':
                    author = Person(value)
                    thesis.author = author
                elif key == u'Fecha de Lectura':
                    thesis.defense_date = datetime.strptime(value, '%d/%m/%Y')
                elif key == u'Departamento':
                    department = session.query(Department).filter_by(name=value).first()
                    if department is None:
                        department = Department(value)
                    thesis.department = department

    session.add(thesis)
    session.commit()

if __name__ == '__main__':
	if len(sys.argv) > 1:
		for file in os.listdir(sys.argv[1]):
			full_path = os.path.join(sys.argv[1], file)

			thesis_id = file.split('.')[0]

			gz_file = gzip.open(full_path)
			scrap_data(gz_file, thesis_id)
			gz_file.close()
	else:
		print 'Data directory not specified'
