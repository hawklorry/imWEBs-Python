from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable
from ...names import Names

class ManureIncorporationWithin48hManagemet(BMPTable):
    """Distribution Table for BMP: Manure incorporation with 48h (21)"""
    __tablename__ = Names.bmp_table_name_manure_incorporation_within_48h_management
    Scenario = Column(Integer)
    Location = Column(Integer)
    FerSurface = Column(REAL)

    def __init__(self):
        self.FerSurface = 0.2

