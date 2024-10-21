from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable
from ...names import Names

class ManureApplicationBasedOnSoliNitrogenLimitManagement(BMPTable):
    """Distribution Table for BMP: Application based on soil nitrogen limit (26)"""
    __tablename__ = Names.bmp_table_name_manure_application_based_on_soil_nitrogen_limit_management
    Scenario = Column(Integer)
    Location = Column(Integer)
    NO3_N_Limit_kg_ha = Column(REAL)
