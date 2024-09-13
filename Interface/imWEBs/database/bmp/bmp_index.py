from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable

class BMP_index(BMPTable):
    __tablename__ = 'BMP_index'
    ID = Column(Integer)
    Name = Column(String)
    Type = Column(Integer)
    CODE = Column(String)