from sqlalchemy import Column, Integer
from .bmp_table import BMPTable


class ManagedAccessIncludingFencingParameter(BMPTable):
    """Parameter Table for BMP: Managed access inluding fencing (40)"""
    __tablename__ = 'managed_access_including_fencing_parameter'
    """Reach ID"""
    ID = Column(Integer, primary_key = True)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Operation starting year"""
    Year = Column(Integer)
