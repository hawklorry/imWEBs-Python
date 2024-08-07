from sqlalchemy import Column, Integer, Float
from .bmp_table import BMPTable

class FieldFarm(BMPTable):
    __tablename__ = 'field_farm'
    ID = Column(Integer, primary_key=True)
    Field = Column(Integer)
    Farm = Column(Integer)
    Area_Ha = Column(Float)
    ToField = Column(Float)
    ToFarm = Column(Float)