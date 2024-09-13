from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable


class PastureCropManagement(BMPTable):
    """Distribution Table for BMP: Pasture crop management (34)"""
    __tablename__ = 'pasture_crop_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    ID = Column(Integer)
    Year = Column(Integer)
    ActualYear = Column(Integer)
    CropCode = Column(Integer)
    PlantingMon = Column(Integer)
    PlantingDay = Column(Integer)
    HarvestMon = Column(Integer)
    HarvestDay = Column(Integer)
    HarvestType = Column(Integer)
    HarvestEfficiency = Column(REAL)
    HarvestIndexOverride = Column(REAL)
    StoverFraction = Column(REAL)
    CNOP = Column(REAL)
    IsGrain = Column(Integer)
    PRCOP = Column(REAL)

    def __init__(self):
        self.Year = 1
        self.ActualYear = 0
        self.CropCode = 27
        self.PlantingMon = 6
        self.PlantingDay = 5
        self.HarvestMon = 8
        self.HarvestDay = 10
        self.HarvestType = 0
        self.HarvestEfficiency = 0.5
        self.HarvestIndexOverride = 0.5
        self.StoverFraction = 0
        self.CNOP = 1
        self.IsGrain = 1
        self.PRCOP = 1

