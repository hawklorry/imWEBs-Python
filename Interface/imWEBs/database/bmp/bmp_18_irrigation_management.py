
from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from .bmp_management_base import BMPManagementBaseWithYear
from ...names import Names

class irrigation_management(BMPManagementBaseWithYear):
    """Distribution Table for BMP: Irrigation management (18)"""

    def __init__(self):
        super().__init__()

        self.IrrMon = 1
        self.IrrDay = 1
        self.Days = 2
        self.IrrType = 0
        self.IrrSource = 0
        self.IrrSourceID = 0
        self.IrrRate = 0
        self.IrrMax = 0
        self.IrrEffi = 0
        self.ReturnFlowCo = 0
        self.WstrMax = 0


class irrigation_parameter(BMPTable):
    """Parameter Table for BMP: Irrigation management (18)"""
    __tablename__ = Names.bmp_table_name_irrigation_parameter
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
