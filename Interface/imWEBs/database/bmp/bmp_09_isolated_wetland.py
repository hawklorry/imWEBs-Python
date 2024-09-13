from typing import Any
from sqlalchemy import Column, Integer, Float, TEXT, REAL, TEXT
from .bmp_table import BMPTable

class Wetland(BMPTable):
    """Parameter Table for BMP: Isolated wetland (9)"""
    __tablename__ = 'wetland'
    ID = Column(TEXT, primary_key=True)
    OperationYear = Column(Integer)
    Subbasin = Column(Integer)
    Type = Column(TEXT)
    ContributionArea_ha = Column(REAL)
    NormalArea_ha = Column(REAL)
    NormalVolume_104M3 = Column(REAL)
    MaxArea_ha = Column(REAL)
    MaxVolume_104M3 = Column(REAL)
    K_mmHr = Column(REAL)
    SedimentConEqui_mgL = Column(REAL)
    D50_um = Column(REAL)
    SettVolN_mYr = Column(REAL)
    SettVolP_mYr = Column(REAL)
    ChlaProCo = Column(REAL)
    WaterCalCo = Column(REAL)
    InflowFrac = Column(REAL)
    InitialVolume_104M3 = Column(REAL)
    InitialSediment_mgL = Column(REAL)
    InitialNO3_mgL = Column(REAL)
    InitialNO2_mgL = Column(REAL)
    InitialNH3_mgL = Column(REAL)
    InitialSolP_mgL = Column(REAL)
    InitialOrgN_mgL = Column(REAL)
    InitialOrgP_mgL = Column(REAL)
    RoutingConstant = Column(REAL)
    WetlandIDOld = Column(Integer)
    ClassType = Column(TEXT)
    SELECTION = Column(Integer)

    def __init__(self):
        self.OperationYear = 0
        self.Type = ""
        self.ContributionArea_ha = 0
        self.NormalArea_ha = 0
        self.NormalVolume_104M3 = 0
        self.MaxArea_ha = 0
        self.MaxVolume_104M3 = 0
        self.K_mmHr = 0
        self.SedimentConEqui_mgL = 0
        self.D50_um = 0
        self.SettVolN_mYr = 0
        self.SettVolP_mYr = 0
        self.ChlaProCo = 0
        self.WaterCalCo = 0
        self.InflowFrac = 0
        self.InitialVolume_104M3 = 0
        self.InitialSediment_mgL = 0
        self.InitialNO3_mgL = 0
        self.InitialNO2_mgL = 0
        self.InitialNH3_mgL = 0
        self.InitialSolP_mgL = 0
        self.InitialOrgN_mgL = 0
        self.InitialOrgP_mgL = 0
        self.RoutingConstant = 0