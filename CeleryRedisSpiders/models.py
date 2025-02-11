# models.py
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Enum, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ProductData(Base):
    __tablename__ = "product_data"


