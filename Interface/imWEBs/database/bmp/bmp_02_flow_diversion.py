
from typing import Any
from sqlalchemy import Column, Integer, REAL, TEXT
from .bmp_table import BMPTable

class FlowDiversion(BMPTable):
    __tablename__ = 'flow_diversion'
    """Flow diversion ID"""
    ID = Column(Integer, primary_key=True)
    """X coordinates"""
    XLL = Column(REAL)
    """Y coordinates"""
    YLL = Column(REAL)
    """Operation date"""
    OPERATION = Column(TEXT)
    """Diversion source type, 0 - outside watershed e.g. deep groundwater, 1 - reach"""
    Source = Column(Integer)
    """Source ID"""
    Source_ID = Column(Integer)
    """Diversion target type, 0 - outside watershed e.g. deep groundwater, 1 - reach"""
    Target = Column(Integer)
    """Target ID"""
    Target_ID = Column(Integer)
    """Diversion rate type, 1 - divert fraction of water in source, 2 - leave minimum volume in source, 3 - divert rate (m3/s)"""
    div_type = Column(Integer)
    """Constant diversion rate (fraction, m3, or m3/s)"""
    Q_REL = Column(REAL)
    """Flow diverting method, i.e. MEA_DIV - diversion using measured rate, CONS_DIV - diversion using constant rate (as Q_REL), MON_CONS_DIV - diversion using constant rate in monthes specified in start_mon and end_mon"""
    METHOD = Column(TEXT)
    """Sediment diverting method"""
    SEDMETHOD = Column(TEXT)
    """Nutrients diverting method"""
    NUTMETHOD = Column(TEXT)
    """Measured data table name in HydroClimate DB (must specify if selecting MEA_DIV method)"""
    FILE = Column(TEXT)
    """Start diversion month (only functional if selecting MON_CONS_DIV method)"""
    start_mon = Column(Integer)
    """End diversion month (only functional if selecting MON_CONS_DIV method)"""
    end_mon = Column(Integer)
    """Diversion channel length (m)"""
    length = Column(REAL)
    """Diversion channel width (m)"""
    width = Column(REAL)
    """Diversion channel main side slope (m/m)"""
    main_side_slope = Column(REAL)
    """Diversion channel floodplain side slope (m/m)"""
    floodplain_side_slope = Column(REAL)
    """Diversion channel main side slope (m/m)"""
    w_ratio = Column(REAL)
    """Diversion channel depth (m)"""
    depth = Column(REAL)
    """Diversion channel average channel slope (m/m)"""
    slope = Column(REAL)
    """Diversion channel manning coefficient"""
    manning = Column(REAL)
    """Diversion channel flow velocity (m/s)"""
    velocity = Column(REAL)
    t0 = Column(REAL)
    d0 = Column(REAL)
    max_elevation = Column(REAL)
    min_elevation = Column(REAL)
    Ave_elevation = Column(REAL)
    erodibility_factor = Column(REAL)
    cover_factor = Column(REAL)
    bc1 = Column(REAL)
    bc2 = Column(REAL)
    bc3 = Column(REAL)
    bc4 = Column(REAL)
    rk1 = Column(REAL)
    rk2 = Column(REAL)
    rk3 = Column(REAL)
    rk4 = Column(REAL)
    rs1 = Column(REAL)
    rs2 = Column(REAL)
    rs3 = Column(REAL)
    rs4 = Column(REAL)
    rs5 = Column(REAL)

    def __init__(self):
        self.XLL = 0
        self.YLL = 0
        self.OPERATION = "1900-01-01"
        self.Source = 1
        self.Source_ID = 0
        self.Target = 1
        self.Target_ID = 0
        self.div_type = 1
        self.Q_REL = 0
        self.METHOD = "CONS_DIV"
        self.SEDMETHOD = ""
        self.NUTMETHOD = ""
        self.FILE = ""
        self.start_mon = 4
        self.end_mon = 10
        self.length = 0
        self.width = 0
        self.main_side_slope = 0
        self.floodplain_side_slope = 0
        self.w_ratio = 0
        self.depth = 0
        self.slope = 0
        self.manning = 0
        self.velocity = 0
        self.t0 = 0
        self.d0 = 0
        self.max_elevation = 0
        self.min_elevation = 0
        self.Ave_elevation = 0
        self.erodibility_factor = 0
        self.cover_factor = 0
        self.bc1 = 0
        self.bc2 = 0
        self.bc3 = 0
        self.bc4 = 0
        self.rk1 = 0
        self.rk2 = 0
        self.rk3 = 0
        self.rk4 = 0
        self.rs1 = 0
        self.rs2 = 0
        self.rs3 = 0
        self.rs4 = 0
        self.rs5 = 0




