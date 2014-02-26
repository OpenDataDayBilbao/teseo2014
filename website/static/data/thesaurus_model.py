# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UnicodeText, Column
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Descriptor(Base):
    __tablename__ = 'descriptor'

    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText, nullable=False)

    parent_code = Column(Integer, ForeignKey('descriptor.id'))
    parent = relationship('Descriptor', remote_side=[id], backref='children')

    def __init__(self, id, text):
        self.id = id
        self.text = text
