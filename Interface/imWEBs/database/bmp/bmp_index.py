from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable
from ...names import Names

class BMP_index(BMPTable):
    __tablename__ = Names.bmp_table_name_bmp_index
    ID = Column(Integer)
    Name = Column(String)
    Type = Column(Integer)
    CODE = Column(String)