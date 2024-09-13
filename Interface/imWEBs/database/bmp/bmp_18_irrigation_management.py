
from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable

class irrigation_management(BMPTable):
    """Distribution Table for BMP: Irrigation management (18)"""
    __tablename__ = 'irrigation_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    Year = Column(Integer)
    IrrMon = Column(Integer)
    IrrDay = Column(Integer)
    Days = Column(Integer)
    IrrType = Column(Integer)
    IrrSource = Column(REAL)
    IrrSourceID = Column(Integer)
    IrrRate = Column(REAL)
    IrrMax = Column(REAL)
    IrrEffi = Column(REAL)
    ReturnFlowCo = Column(REAL)
    WstrMax = Column(REAL)

class irrigation_parameter(BMPTable):
    """Parameter Table for BMP: Irrigation management (18)"""
    __tablename__ = 'irrigation_parameter'
    IrrType = Column(Integer,primary_key=True)
    IRRNM = Column(TEXT)
    Year = Column(Integer)
    IrrMon = Column(Integer)
    IrrDay = Column(Integer)
    IrrSource = Column(REAL)
    IrrSourceID = Column(Integer)
    IrrRate = Column(REAL)
    IrrMax = Column(REAL)
    IrrEffi = Column(REAL)
    ReturnFlowCo = Column(REAL)
    WstrMax = Column(REAL)

    def __init__(self):
        self.Year = 1
        self.IrrMon = 5
        self.IrrDay = 10
        self.Days = 1
        self.IrrType = 2
        self.IrrSource = 4
        self.IrrSourceID = 0
        self.IrrRate = 200
        self.IrrMax = 20
        self.IrrEffi = 1
        self.ReturnFlowCo = 0
        self.WstrMax = 0.9
