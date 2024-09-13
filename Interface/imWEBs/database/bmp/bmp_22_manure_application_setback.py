from sqlalchemy import Column, Integer
from .bmp_table import BMPTable

class ManureApplicationSetbackManagement(BMPTable):
    """Distribution Table for BMP: Manure application setback (22)"""
    __tablename__ = 'manure_application_setback_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
