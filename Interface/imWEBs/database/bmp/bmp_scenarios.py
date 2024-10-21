from sqlalchemy import Column, Integer, Float, String, Double
from .bmp_table import BMPTable
from ...bmp.bmp import BMPType

class BMP_scenarios(BMPTable):
    __tablename__ = 'BMP_scenarios'
    ID = Column(String)
    NAME = Column(String)
    BMP = Column(Integer)
    DISTRIBUTION = Column(String)
    PARAMETER = Column(String)

    def __init__(self, bmp_type:BMPType, distribution:str, parameter:str):
        self.BMP = bmp_type.value
        self.DISTRIBUTION = distribution
        self.PARAMETER = parameter
        self.ID = -1
        self.NAME = "scenario"
        