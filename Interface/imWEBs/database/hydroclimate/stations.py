from sqlalchemy import Column, Integer, REAL, TEXT
from .hydroclimate_table import HydroClimateTable

class Stations(HydroClimateTable):
    __tablename__ = 'STATIONS'
    ID = Column(Integer, primary_key=True)
    NAME = Column(TEXT)
    XPR = Column(REAL)
    YPR = Column(REAL)
    LAT = Column(REAL)
    LONG = Column(REAL)
    ELEVATION = Column(REAL)
    AREA = Column(REAL)