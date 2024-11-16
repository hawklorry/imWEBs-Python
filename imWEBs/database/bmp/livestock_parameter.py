from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable
from ...names import Names

class Livestock_Parameter(BMPTable):
    __tablename__ = Names.bmp_table_name_livestock_parameter
    """Animal ID"""
    ID = Column(Integer, primary_key=True)
    """Animal name"""
    Name = Column(String)
    """Description"""
    Description = Column(String)
    """Manure ID corresponding the fertilizer table"""
    Man_ID = Column(Integer)
    """Animal weight"""
    Ani_Weight = Column(Double)
    """Fresh manure production per 1000kg live animal mass per day"""
    Man_Day = Column(Double)
    """Dry mass intake per day in percent of body weight"""
    Mass_Intake = Column(Double)
    """Average non-adult weight / adult weight"""
    Ani_nonadult = Column(Double)
    """TSS percentage of the manure """
    Man_TSS_Fra = Column(Double)