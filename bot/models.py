from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BreadStock(Base):
    __tablename__ = 'bread_stock'

    id = Column(Integer, primary_key = True)
    availability = Column(String(80))