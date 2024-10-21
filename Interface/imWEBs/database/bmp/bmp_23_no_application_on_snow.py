from sqlalchemy import Column, Integer
from .bmp_table import BMPTable
from ...names import Names

class ManureNoApplicaitonOnSnowManagement(BMPTable):
    """Distribution Table for BMP: No application on snow (23)"""
    __tablename__ = Names.bmp_table_name_manure_no_application_on_snow_management
    Scenario = Column(Integer)
    Location = Column(Integer)
    StartYear = Column(Integer)
    StartMon = Column(Integer)
    StartDay = Column(Integer)
    EndYear = Column(Integer)
    EndMon = Column(Integer)
    EndDay = Column(Integer)
    IsAnnually = Column(Integer)

