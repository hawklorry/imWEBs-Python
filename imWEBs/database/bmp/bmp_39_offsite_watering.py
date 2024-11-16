from sqlalchemy import Column, Integer
from .bmp_table import BMPTable
from ...names import Names

class OffsiteWateringParameter(BMPTable):
    """Parameter Table for BMP: Off site watering (39)"""
    __tablename__ = Names.bmp_table_name_offsite_watering
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

    def __init__(self, id:int, subbasin:int):
        self.ID = id
        self.Year = 0
        self.Subbasin = subbasin
        self.SourceID = subbasin
        self.Source = 0

