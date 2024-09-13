from sqlalchemy import Column, Integer
from .bmp_table import BMPTable


class ManureSpringApplicationRatherThanFallApplicationManagement(BMPTable):
    """Distribution Table for BMP: Spring application rather than fall application (24)"""
    __tablename__ = 'manure_spring_application_rather_than_fall_application_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    StartYear = Column(Integer)
    StartMon = Column(Integer)
    StartDay = Column(Integer)
    EndYear = Column(Integer)
    EndMon = Column(Integer)
    EndDay = Column(Integer)
    IsAnnually = Column(Integer)
