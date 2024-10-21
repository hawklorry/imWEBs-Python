from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable
from ...names import Names

class RiparianBuffer(BMPTable):
    """Distribution Table for BMP: Riparian buffer (5)"""
    __tablename__ = Names.bmp_table_name_riparian_buffer

    """Scenario ID"""
    Scenario = Column(Integer)
    """Riparian buffer drainage part id used for IMWEBs model calculation, one RIBUF may contain several drainage parts"""
    ID = Column(Integer)
    """Year of operation"""
    Year = Column(Integer)
    """Group riparian buffer ID"""
    RIBUF_ID = Column(Integer)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Vegetation ID"""
    VegetationID = Column(Integer)
    """Length of the riparian buffer (m)"""
    Length = Column(REAL)
    """Width of the riparian buffer (m)"""
    Width = Column(REAL)
    """Area of the riparian buffer (ha)"""
    Area_ha = Column(REAL)
    """Drainage area (ha)"""
    Drainage_Area = Column(REAL)
    """Riparian buffer drainage area to riparian buffer area ratio"""
    Area_Ratio = Column(REAL)
    """Slope of the riparian buffer (%)"""
    Slope = Column(REAL)
    """Riparian buffer soil saturation hydraulic conductivity (mm/hr)"""
    Sol_K = Column(REAL)
    """Riparian buffer soil porosity"""
    Sol_porosity = Column(REAL)
    """Riparian buffer root depth (mm)"""
    Root_Depth = Column(REAL)

    def __init__(self):
        self.Year = 1
        self.RIBUF_ID = 0
        self.Subbasin = 0
        self.VegetationID = 6
        self.Length = 0
        self.Width = 0
        self.Area_ha = 0
        self.Drainage_Area = 0
        self.Area_Ratio = 0
        self.Slope = 0
        self.Sol_K = 0.25
        self.Sol_porosity = 0
        self.Root_Depth = 0
