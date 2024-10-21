from sqlalchemy import Column, Integer
from .bmp_table import BMPTable
from ...names import Names

class ManagedAccessIncludingFencingParameter(BMPTable):
    """Parameter Table for BMP: Managed access inluding fencing (40)"""
    __tablename__ = Names.bmp_table_name_managed_access_including_fencing
    """Reach ID"""
    ID = Column(Integer, primary_key = True)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Operation starting year"""
    Year = Column(Integer)
