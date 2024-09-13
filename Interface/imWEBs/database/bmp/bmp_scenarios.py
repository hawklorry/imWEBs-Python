from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable

class BMP_scenarios(BMPTable):
    __tablename__ = 'BMP_scenarios'
    ID = Column(String)
    NAME = Column(String)
    BMP = Column(String)
    DISTRIBUTION = Column(String)
    PARAMETER = Column(String)