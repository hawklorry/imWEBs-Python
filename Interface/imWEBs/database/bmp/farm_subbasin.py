from sqlalchemy import Column, Integer, Float
from .bmp_table import BMPTable

class FarmSubbasin(BMPTable):
    __tablename__ = 'farm_subbasin'
    ID = Column(Integer, primary_key=True)
    Farm = Column(Integer)
    Subbasin = Column(Integer)
    Area_Ha = Column(Float)
    ToFarm = Column(Float)
    ToSubbasin = Column(Float)
