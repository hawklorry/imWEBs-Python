from typing import Any
from sqlalchemy import Column, Integer, Float, TEXT, REAL
from .bmp_table import BMPTable
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

class WinteringSiteManagement(BMPTable):
    """Distribution Table for BMP: Wintering site management (33)"""
    __tablename__ = Names.bmp_table_name_wintering_site_management
    """Scenario ID"""
    Scenario = Column(Integer)
    """Location ID"""
    Location = Column(Integer)
    """BMP start year"""
    Year = Column(Integer)
    """BMP start month"""
    GraMon = Column(Integer)
    """BMP start day"""
    GraDay = Column(Integer)
    """BMP lasting days"""
    Days = Column(Integer)
    """Animal ID"""
    Ani_ID = Column(Integer)
    """Adult animal percentage"""
    Ani_adult = Column(Integer)
    """Grazing density (1/ha)"""
    GR_Density = Column(REAL)
    """Fraction of day animal stay in field"""
    DayFra = Column(REAL)
    """Water source type, 0 - outside watershed e.g. deep groundwater, 1 - reach, 2 - reservoir, 3 - catch basin, 4 - groundwater, 5 - wetland, 6 - dugout"""
    Source = Column(Integer)
    """Water source ID"""
    SourceID = Column(Integer)
    """Dugout IDs in the grazing area"""
    Dugout_ID = Column(Integer)
    """0 – accessible, 1 – managed access, 2 – no access"""
    Access = Column(Integer)
    """0 – no fencing, 1- fencing"""
    Fencing = Column(Integer)
    """Percent of animals drinking in streams. Default is 1"""
    StreamAniPerc = Column(Float)
    """Percent of day time for drinking, default is 0.02 (0.5/24)"""
    Drinking_time = Column(Float)
    """Average bank erodibility change compared to no-fencing """
    BankK_Change = Column(Float)

    def __init__(self):
        self.Year = 1
        self.GraMon = 9
        self.GraDay = 1
        self.Days = 45
        self.Ani_ID = 1
        self.Ani_adult = 50
        self.GR_Density = 15
        self.DayFra = 0.3
        self.Source = 1
        self.SourceID = 0
        self.Dugout_ID = 0
        self.Access = 0
        self.Fencing = 0
        self.StreamAniPerc = 1
        self.Drinking_time = 0.02
        self.BankK_Change = 0.3


class manure_and_nutrient_management(BMPTable):
    __tablename__ = 'manure_and_nutrient_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    ID = Column(Integer)
    Level = Column(TEXT)
    BMP_ID = Column(Integer)
    Parameter = Column(REAL)
    Value = Column(REAL)

class manure_and_nutrient_parameter(BMPTable):
    __tablename__ = 'manure_and_nutrient_parameter'
    BMP_ID = Column(Integer, primary_key=True)
    Code = Column(TEXT)
    Description = Column(TEXT)
    Parameter = Column(TEXT)
    Value = Column(REAL)
    Value_TEXT = Column(TEXT)





