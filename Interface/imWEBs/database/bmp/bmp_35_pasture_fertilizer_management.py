from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable


class PastureFertilizerManagement(BMPTable):
    """Distribution Table for BMP: Pasture fertilizer management (35)"""
    __tablename__ = 'pasture_fertilizer_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    Year = Column(Integer)
    FerMon = Column(Integer)
    FerDay = Column(Integer)
    FerType = Column(Integer)
    FerRate = Column(REAL)
    FerSurface = Column(REAL)

    def __init__(self):
        self.Year = 1
        self.FerMon = 8
        self.FerDay = 10
        self.FerType = 1
        self.FerRate = 500
        self.FerSurface = 0.3
