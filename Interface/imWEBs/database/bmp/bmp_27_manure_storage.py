
from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable

class ManureStorageParameter(BMPTable):
    """Parameter Table for BMP: Manure storage capacity and design (27)"""
    __tablename__ = 'manure_storage_parameter'
    """Manure storage ID"""    
    ManStorageID = Column(Integer,primary_key=True)
    """Name"""
    Name = Column(TEXT)
    """Description"""
    Description = Column(TEXT)
    """Producer ID"""
    ProducerID = Column(Integer)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Corresponding feedlot ID"""
    FeedlotID = Column(Integer)
    """Length of the manure storage (m)"""
    ManLength_m = Column(REAL)
    """Width of the Manure storage (m)"""
    ManWidth_m = Column(REAL)
    """Area of the Manure storage (m2)"""
    ManArea_m2 = Column(REAL)
    """Drainage area of the manure storage (ha)"""
    DraArea_ha = Column(REAL)
    """Manure drainage area fraction of the subbasin area (-)"""
    DraFraction = Column(REAL)
    """Distance to the nearby stream"""
    DisReach_m = Column(REAL)
    """Height to the nearby stream"""
    HigReach_m = Column(REAL)
    """Threshold value of storage distance to the nearby stream (100m)"""
    ThDisReach = Column(REAL)
    """Threshold value of storage height to the nearby stream (10m)"""
    ThHigReach = Column(REAL)
    """Initial storage (kg)"""
    ManInitial = Column(REAL)
    """CN change fraction compared to non-storage area"""
    CN_change = Column(REAL)
    """PRC change fraction compared to non-storage area"""
    PRC_change = Column(REAL)
    """Manure event mean concentration (mg/l)"""
    Manure_EMC = Column(REAL)

    def __init__(self):
        self.ManLength_m = 20
        self.ManWidth_m = 20
        self.ManArea_m2 = 400
        self.DraArea_ha = 0
        self.DraFraction = 1
        self.HigReach_m = 0
        self.DisReach_m = 0
        self.ThDisReach = 0
        self.ThHigReach = 0
        self.ManInitial = 0
        self.CN_change = 0.3
        self.PRC_change = 0.3
        self.Manure_EMC = 10000


class ManureStorageManagement(BMPTable):
    """Distribution Table for BMP: Manure storage capacity and design (27)"""
    __tablename__ = 'manure_storage_management'

    """Scenario ID"""
    Scenario = Column(Integer)
    """Manure Storage ID"""
    Location = Column(Integer)
    """nan"""
    Year = Column(Integer)
    """Month of manure application"""
    ManAppMon = Column(Integer)
    """Day of manure application"""
    ManAppDay = Column(Integer)
    """Fraction of manure amount applied to the field"""
    ManAppFra = Column(Integer)

    def __init__(self):
        self.Year = 0
        self.ManAppMon = 11
        self.ManAppDay = 15
        self.ManAppFra = 1


