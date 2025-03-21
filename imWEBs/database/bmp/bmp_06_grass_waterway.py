
from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable
from ...names import Names

class GrassWaterWay(BMPTable):
    """Parameter Table for BMP: Grass waterway (6)"""
    __tablename__ = Names.bmp_table_name_grass_waterway
    """Riparian buffer drainage part id used for IMWEBs model calculation, one RIBUF may contain several drainage parts"""
    ID = Column(Integer, primary_key=True)
    """Year of operation"""
    Year = Column(Integer)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """GWW length (m)"""
    Length = Column(REAL)
    """GWW bankfull width (m), default is 10 m"""
    BFwidth = Column(REAL)
    """GWW bankfull depth (m), default is 0.5 m"""
    BFdepth = Column(REAL)
    """GWW channel side slope, default is 0.25 (1:4)"""
    SideSlope = Column(REAL)
    """GWW channel slope (%)"""
    Slope_perc = Column(REAL)
    """GWW roughness coefficient, default is 0.25"""
    Manning = Column(REAL)
    """GWW bankfull velocity (m/s)"""
    BFvelocity = Column(REAL)
    """GWW bottom conductivity (mm/hr), default is 10"""
    Conductivity = Column(REAL)
    """GWW erodibility factor, default is 0"""
    Erodibility = Column(REAL)
    """GWW cover factor, default is 0"""
    Cover = Column(REAL)

    def __init__(self, id:int, subbasin:int, length: float):
        self.ID = id
        self.Year = 1900
        self.Subbasin = subbasin
        self.Length = length
        self.BFwidth = 10
        self.BFdepth = 0.5
        self.SideSlope = 0.25
        self.Slope_perc = 0
        self.Manning = 0.25
        self.BFvelocity = 0
        self.Conductivity = 10
        self.Erodibility = 0
        self.Cover = 0

