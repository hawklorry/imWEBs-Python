from sqlalchemy import Column, Integer, Float
from .bmp_table import BMPTable

class FieldSubbasin(BMPTable):
    __tablename__ = 'field_subbasin'
    ID = Column(Integer, primary_key=True)
    Field = Column(Integer)
    Subbasin = Column(Integer)
    Area_Ha = Column(Float)
    ToField = Column(Float)
    ToSubbasin = Column(Float)