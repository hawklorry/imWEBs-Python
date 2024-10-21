from typing import Any
from sqlalchemy import Column, Integer, REAL, TEXT
from .bmp_table import BMPTable
from ...names import Names
from ...delineation.structure_attribute import StructureAttribute

class Wascob(BMPTable):
    """Parameter Table for BMP: WASCob (41)"""
    __tablename__ = Names.bmp_table_name_wascob

    Scenario = Column(Integer)
    ID = Column(Integer)

    StartYear = Column(Integer)
    StartMon = Column(Integer)
    StartDay = Column(Integer)

    FieldId = Column(Integer)
    OutletReachId = Column(Integer)

    BermElevation = Column(REAL)

    DeadVolume = Column(REAL)
    DeadArea = Column(REAL)

    NormalVolume = Column(REAL)
    NormalArea = Column(REAL)

    MaxVolume = Column(REAL)
    MaxArea = Column(REAL)
    
    ContributionArea = Column(REAL)
    DischargeCapacity = Column(REAL)

    TileOutflowCoefficient = Column(REAL)
    SpillwayDecay = Column(REAL)

    K = Column(REAL)
    Nsed = Column(REAL)
    D50 = Column(REAL)
    Dcc = Column(REAL)

    PSettle = Column(REAL)
    NSettle = Column(REAL)
    Chlaw = Column(REAL)
    Secciw = Column(REAL)

    InitialVolume = Column(REAL)
    InitialSedimentConc = Column(REAL)

    InitialSolPConc = Column(REAL)
    InitialOrgPConc = Column(REAL)

    InitialNO3Conc = Column(REAL)
    InitialOrgNConc = Column(REAL)
    InitialNO2Conc = Column(REAL)
    InitialNH3Conc = Column(REAL)

    BermType = Column(TEXT)

    def __init__(self,attribute:StructureAttribute = None):
        self.Scenario = -1
        self.ID = attribute.id
        self.ContributionArea = attribute.contribution_area

        self.StartYear = 1900
        self.StartMon = 1
        self.StartDay = 1
        self.DeadArea = 0
        self.DeadVolume = 0
        self.TileOutflowCoefficient = 1
        self.SpillwayDecay = 1
        self.K = 2.5
        self.Nsed = 1
        self.D50 = 10
        self.Dcc = 0.185
        self.PSettle = 10
        self.NSettle = 10
        self.Chlaw = 1
        self.Secciw = 1
        self.InitialVolume = 0
        self.InitialSedimentConc = 0
        self.InitialSolPConc = 0.05
        self.InitialOrgPConc = 0.05
        self.InitialNO3Conc = 0.5
        self.InitialOrgNConc = 0.5
        self.InitialNO2Conc = 0.1
        self.InitialNH3Conc = 0.1
        self.BermType = ''
