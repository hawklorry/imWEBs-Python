from typing import Any
from sqlalchemy import Column, Integer, Float, TEXT, REAL
from .bmp_table import BMPTable
from .bmp_16_grazing_management import GrazingManagement
from ...names import Names

class WinteringSiteParameter(BMPTable):
    """Parameter Table for Wintering Site Management"""

    __tablename__ = Names.bmp_table_name_wintering_site_parameter

    """Wintering site ID"""
    ID = Column(Integer, primary_key=True)

    """Producer ID"""
    ProducerID = Column(Integer)

    """Wintering site area (ha)"""
    Area_Ha = Column(Float)

    """Slope of the Wintering site area (%)"""
    Slope = Column(Float)

    """Distance to creek (m)"""
    Distance_m = Column(Float)

class WinteringSiteManagement(GrazingManagement):
    """Distribution Table for BMP: Wintering site management (33)"""
    def __init__(self):
        super().__init__()


# class manure_and_nutrient_management(BMPTable):
#     __tablename__ = 'manure_and_nutrient_management'
#     Scenario = Column(Integer)
#     Location = Column(Integer)
#     ID = Column(Integer)
#     Level = Column(TEXT)
#     BMP_ID = Column(Integer)
#     Parameter = Column(REAL)
#     Value = Column(REAL)

# class manure_and_nutrient_parameter(BMPTable):
#     __tablename__ = 'manure_and_nutrient_parameter'
#     BMP_ID = Column(Integer, primary_key=True)
#     Code = Column(TEXT)
#     Description = Column(TEXT)
#     Parameter = Column(TEXT)
#     Value = Column(REAL)
#     Value_TEXT = Column(TEXT)





