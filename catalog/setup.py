import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class LapyUser(Base):
    __tablename__ = 'lapyuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(203), nullable=False)
    email = Column(String(213), nullable=False)


class Laptop(Base):
    __tablename__ = 'laptop'
    id = Column(Integer, primary_key=True)
    name = Column(String(278), nullable=False)
    user_id = Column(Integer, ForeignKey('lapyuser.id'))
    user = relationship(LapyUser, backref="laptop")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class Types(Base):
    __tablename__ = 'types'
    id = Column(Integer, primary_key=True)
    lapyname = Column(String(157), nullable=False)
    speciality = Column(String(467))
    ram = Column(String(32))
    storage = Column(String(24))
    price = Column(String(100000))
    warrenty = Column(String(20))
    rating = Column(String(150))
    date = Column(DateTime, nullable=False)
    laptopid = Column(Integer, ForeignKey('laptop.id'))
    laptop = relationship(
        Laptop, backref=backref('types', cascade='all, delete'))
    lapyuser_id = Column(Integer, ForeignKey('lapyuser.id'))
    lapyuser = relationship(LapyUser, backref="types")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'lapyname': self.lapyname,
            'speciality': self.speciality,
            'ram': self.ram,
            'storage': self.storage,
            'warrenty': self.warrenty,
            'price': self.price,
            'rating': self.rating,
            'date': self.date,
            'id': self. id
        }

engin = create_engine('sqlite:///laptop.db')
Base.metadata.create_all(engin)
