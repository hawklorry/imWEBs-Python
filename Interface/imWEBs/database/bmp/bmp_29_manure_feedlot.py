from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable

class ManureFeedlotParameter(BMPTable):
    """Parameter Table for BMP: Manure feedlot (29)"""
    __tablename__ = 'manure_feed_lot_parameter'
    """ID"""
    ID = Column(Integer, primary_key = True)
    """Name"""
    Name = Column(TEXT)
    """Description"""
    Description = Column(TEXT)
    """Producer ID. Not used in the module"""
    ProducerID = Column(Integer)
    """Subbasin. Not used in the module"""
    Subbasin = Column(Integer)
    """The id of animal whose parameter could be found in livestok_parameter table"""
    AniID = Column(Integer)
    """The id of catch basin which the feedlot would drains to."""
    CatBasID = Column(Integer)
    """Initial manure storage of the feedlot"""
    ManInitial = Column(REAL)
    """Average CN increase fraction compare to non-feedlot area"""
    CN_change = Column(REAL)
    """Average PRC increase fraction compare to non-feedlot area"""
    PRC_change = Column(REAL)
    """Manure event mean concentration"""
    Manure_EMC = Column(REAL)

    def __init__(self):
        self.ManInitial = 0
        self.CN_change = 0.2
        self.PRC_change = 0.2
        self.Manure_EMC = 100000

class ManureFeedlotManagement(BMPTable):
    """Distribution Table for BMP: Manure feedlot (29)"""
    __tablename__ = 'manure_feed_lot_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    Year = Column(Integer)
    FDLMon = Column(Integer)
    FDLDay = Column(Integer)
    Days = Column(Integer)
    """Number of adult animals"""
    AniAdult = Column(Integer)
    """Number of non-adult animals"""
    AniNonAdult = Column(Integer)
    ManStoID = Column(TEXT)
    ManStoDis = Column(TEXT)
    ManRemMon = Column(Integer)
    ManRemDay = Column(Integer)
    ManRemFra = Column(REAL)

    def __init__(self):
        self.Year = 1
        self.FDLMon = 1
        self.FDLDay = 1
        self.Days = 120
        #user should provide the nunbre of adult and non-adult
        self.AniAdult = 0
        self.AniNonAdult = 0
        
        self.ManStoDis = 1
        self.ManRemMon = 10
        self.ManRemDay = 31
        self.ManRemFra = 1
