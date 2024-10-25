from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from ...delineation.structure_attribute import StructureAttribute
from .bmp_management_base import BMPManagementBaseWithYear
from ...names import Names

class ManureFeedlot(BMPTable):
    """Parameter Table for BMP: Manure feedlot (29)"""
    __tablename__ = Names.bmp_table_name_manure_feed_lot_parameter
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

    def __init__(self, attribute:StructureAttribute = None):
        if attribute is not None:
            self.ID = attribute.id
            self.ProducerID = self.ID
            self.Subbasin = attribute.subbasin

        self.CatBasID = 0

        self.AniID = 1
        self.ManInitial = 0
        self.CN_change = 0.2
        self.PRC_change = 0.2
        self.Manure_EMC = 100000

class ManureFeedlotManagement(BMPManagementBaseWithYear):
    """Distribution Table for BMP: Manure feedlot (29)"""

    #FDLMon,FDLDay,Days,AniAdult,AniNonAdult,ManStoID,ManStoDis,ManRemMon,ManRemDay,ManRemFra"
    def __init__(self):
        super().__init__()
        self.FDLMon = 1
        self.FDLDay = 1
        self.Days = 120

        """Number of adult animals"""
        self.AniAdult = 0
        """Number of non-adult animals"""
        self.AniNonAdult = 0

        self.ManStoID = 0
        self.ManStoDis = 1

        self.ManRemMon = 10
        self.ManRemDay = 31
        self.ManRemFra = 1
