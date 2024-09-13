from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable

class ManureApplicationBasedOnPhosphorousLimitManagement(BMPTable):
    """Distribution Table for BMP: Application based on soil Phosphorous limit (25)"""
    __tablename__ = 'manure_application_based_on_soil_phosphorous_limit_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    Soil_P_Limit_kg_ha = Column(REAL)
