from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable

class ManureCatchBasin(BMPTable):
    """Parameter Table for BMP: Manure catch basin/impondment (28)"""
    __tablename__ = 'manure_catch_basin'
    ID = Column(Integer, primary_key = True)
    OperationYear = Column(Integer)
    Subbasin = Column(Integer)
    receive_reach_id = Column(Integer)
    MaxL_m = Column(REAL)
    MaxW_m = Column(REAL)
    MaxD_m = Column(REAL)
    SideSlope = Column(REAL)
    EndSlope = Column(REAL)
    MaxVolume_104M3 = Column(REAL)
    FDLT_Ratio = Column(REAL)
    NonFDLT_Ratio = Column(REAL)
    NSED = Column(REAL)
    CB_Dcc = Column(REAL)
    SettVolP_mYr = Column(REAL)
    SettVolN_mYr = Column(REAL)
    K_mmHr = Column(REAL)
    CHLAR = Column(REAL)
    SECCIR = Column(REAL)
    InitialVolume = Column(REAL)
    InitialSediment_mgL = Column(REAL)
    InitialNO3_mgL = Column(REAL)
    InitialSolP_mgL = Column(REAL)
    InitialOrgN_mgL = Column(REAL)
    InitialOrgP_mgL = Column(REAL)

    def __init__(self):
        self.OperationYear = 0
        self.MaxL_m = 100
        self.MaxW_m = 50
        self.MaxD_m = 10
        self.SideSlope = 1.5
        self.EndSlope = 4
        self.MaxVolume_104M3 = 2.3
        self.FDLT_Ratio = 1
        self.NonFDLT_Ratio = 0
        self.NSED = 5
        self.CB_Dcc = 0.184
        self.SettVolP_mYr = 10
        self.SettVolN_mYr = 10
        self.K_mmHr = 0.05
        self.CHLAR = 1
        self.SECCIR = 1
        self.InitialVolume = 100
        self.InitialSediment_mgL = 5
        self.InitialNO3_mgL = 0.5
        self.InitialSolP_mgL = 0.05
        self.InitialOrgN_mgL = 0.5
        self.InitialOrgP_mgL = 0.05
