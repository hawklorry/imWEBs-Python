from sqlalchemy import Column, Integer, Float, String
from .bmp_table import BMPTable

class FieldInfo(BMPTable):
    __tablename__ = 'field_info'
    ID = Column(Integer, primary_key=True)
    Area_Ha = Column(Float)

    def __init__(self, id, area_ha):
        self.ID = id
        self.Area_Ha = area_ha