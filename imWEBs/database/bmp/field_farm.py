from sqlalchemy import Column, Integer, Float
from .bmp_table import BMPTable
from ...names import Names

class FieldFarm(BMPTable):
    __tablename__ = Names.bmp_table_name_field_farm
    ID = Column(Integer, primary_key=True)
    Field = Column(Integer)
    Farm = Column(Integer)
    Area_Ha = Column(Float)
    ToField = Column(Float)
    ToFarm = Column(Float)