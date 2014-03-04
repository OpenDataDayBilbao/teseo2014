# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UnicodeText, Boolean, Date, create_engine, Column
from sqlalchemy import Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()

class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    location = Column(UnicodeText, nullable=True)
    private = Column(Boolean, nullable=True, default=False)

    def __init__(self, name, location=None, private=None):
        self.name = name
        self.location = location

class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)

    def __init__(self, name):
        self.name = name

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    first_name = Column(UnicodeText, nullable=True)
    first_surname = Column(UnicodeText, nullable=True)
    second_surname = Column(UnicodeText, nullable=True)
    gender = Column(UnicodeText, nullable=True)

    def __init__(self, name, first_name=None, first_surname=None, second_surname=None, gender=None):
        self.name = name
        self.first_name = first_name
        self.first_surname = first_surname
        self.second_surname = second_surname
        self.gender = gender

class Descriptor(Base):
    __tablename__ = 'descriptor'

    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText, nullable=False)
    code = Column(Integer, nullable=True)

    parent_code = Column(Integer, ForeignKey('descriptor.id'))
    parent = relationship('Descriptor', remote_side=[id], backref='children')

    def __init__(self, text, code=None):
        self.text = text
        self.code = code

class Advisor(Base):
    __tablename__ = 'advisor'

    thesis_id = Column(Integer, ForeignKey('thesis.id', ondelete='cascade'), primary_key=True)
    thesis = relationship("Thesis")

    person_id = Column(Integer, ForeignKey('person.id', ondelete='cascade'), primary_key=True)
    person = relationship("Person")

    role = Column(UnicodeText, nullable=False)

    def __init__(self, person, role):
        self.person = person
        self.role = role

class PanelMember(Base):
    __tablename__ = 'panel_member'

    thesis_id = Column(Integer, ForeignKey('thesis.id', ondelete='cascade'), primary_key=True)
    thesis = relationship("Thesis")

    person_id = Column(Integer, ForeignKey('person.id', ondelete='cascade'), primary_key=True)
    person = relationship("Person")

    role = Column(UnicodeText, nullable=False)

    def __init__(self, person, role):
        self.person = person
        self.role = role

association_thesis_description = Table('association_thesis_description',
    Base.metadata,
    Column('thesis_id', Integer, ForeignKey('thesis.id', ondelete='cascade')),
    Column('descriptor_id', Integer, ForeignKey('descriptor.id', ondelete='cascade'))
)

class Thesis(Base):
    __tablename__ = 'thesis'

    id = Column(Integer, primary_key=True)
    title =  Column(UnicodeText, nullable=False)

    def __init__(self, id=None):
        self.id = id

    author_id = Column(Integer, ForeignKey('person.id'))
    author = relationship('Person')

    defense_date = Column(Date, nullable=False)

    university_id = Column(Integer, ForeignKey('university.id'))
    university = relationship('University')

    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship('Department')

    advisors = relationship('Advisor')
    panel = relationship('PanelMember')

    descriptors = relationship('Descriptor',
            secondary=association_thesis_description)

    summary = Column(UnicodeText)

if __name__ == '__main__':
    # USER = 'teseo'
    # PASS = 'teseo'

    # DB_NAME = 'teseo'

    # engine = create_engine('mysql://%s:%s@localhost/%s?charset=utf8' % (USER, PASS, DB_NAME))

    engine = create_engine('sqlite:///minotaur.db')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
