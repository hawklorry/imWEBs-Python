from typing import Any
from sqlalchemy import Column, Integer
from .bmp_table import BMPTable
from ...names import Names

class Pasture_tillage_management(BMPTable):
    """Distribution Table for BMP: Pasture tillage management (36)"""
    __tablename__ = Names.bmp_table_name_pasture_tillage_management
    Scenario = Column(Integer)
    Location = Column(Integer)
    Year = Column(Integer)
    TillMon = Column(Integer)
    TillDay = Column(Integer)
    TillCode = Column(Integer)

    def __init__(self):
        self.Year = 1
        self.TillMon = 5
        self.TillDay = 10
        self.TillCode = 1
