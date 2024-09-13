from sqlalchemy import Column, Integer
from .bmp_table import BMPTable


class OffsiteWateringParameter(BMPTable):
    """Parameter Table for BMP: Off site watering (39)"""
    __tablename__ = 'offsite_watering_parameter'
    """Off-site watering ID"""
    ID = Column(Integer, primary_key = True)
    """Operation starting year (designed for setting up dugout scenarios)"""
    Year = Column(Integer)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Water source type,  1 - reach, 2 - reservoir, 3 - catch basin, 4 - groundwater, 5 - wetland, 6 - dugout"""
    Source = Column(Integer)
    """ID for the source"""
    SourceID = Column(Integer)
