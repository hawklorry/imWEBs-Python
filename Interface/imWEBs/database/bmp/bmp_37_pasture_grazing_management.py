from .bmp_16_grazing_management import GrazingManagement
from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from ...names import Names

class PastureGrazingManagement(GrazingManagement):
    """Distribution Table for BMP: Pasture grazing management (37)"""
    def __init__(self):
        super().__init__()


class PastureGrazingParameter(BMPTable):
    """Distribution Table for BMP: Pasture grazing management (37)"""
    __tablename__ = Names.bmp_table_name_pasture_grazing_parameter
    """Pasture grazing land ID"""
    ID = Column(Integer, primary_key=True)
    """Producer ID"""
    ProducerID = Column(Integer)
    """Pasture grazing area (ha)"""
    Area_ha = Column(REAL)