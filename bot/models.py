from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CountryLoaf(Base):
    __tablename__ = 'country_loaf'

    id = Column(Integer, primary_key = True)
    datetime = Column(String(80))
    date = Column(String(80))
    time = Column(String(80))
    availability = Column(String(80))