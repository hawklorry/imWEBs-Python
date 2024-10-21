from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from ...names import Names

class TileDrainParameter(BMPTable):
    """Parameter Table for BMP: till drainge management (19)"""
    __tablename__ = Names.bmp_table_name_tile_drain_parameter
    Scenario = Column(Integer)
    Id = Column(Integer)
    StartYear = Column(Integer)
    StartMon = Column(Integer)
    StartDay = Column(Integer)
    FieldId = Column(Integer)
    OutletReachId = Column(Integer)
    Type = Column(Integer)
    Elevation = Column(REAL)
    Depth = Column(REAL)
    ControlDepth = Column(REAL)
    ControlStartMon = Column(REAL)
    ControlEndMon = Column(REAL)
    Radius = Column(REAL)
    Spacing = Column(REAL)
    OutletCapacity = Column(REAL)
    LagCoefficient = Column(REAL)
    DepthToImperviableLayer = Column(REAL)
    LateralKScale = Column(REAL)
    SedimentCon = Column(REAL)
    OrgNConc = Column(REAL)
    OrgPConc = Column(REAL)
    PRCTile = Column(REAL)
    CNTile = Column(REAL)
    GWT0 = Column(REAL)

    def __init__(self):
        self.StartYear = 1900
        self.StartMon = 1
        self.StartDay = 1
        self.Type = 0
        self.Depth = 914.4
        self.ControlDepth = 500
        self.ControlStartMon = 4
        self.ControlEndMon = 10
        self.Radius = 50
        self.Spacing = 12192
        self.LagCoefficient = 0.9
        self.DepthToImperviableLayer = 1500
        self.LateralKScale = 1
        self.SedimentCon = 100
        self.OrgNConc = 10
        self.OrgPConc = 10
        self.PRCTile = 0.75
        self.CNTile = 0.75
        self.GWT0 = 300

