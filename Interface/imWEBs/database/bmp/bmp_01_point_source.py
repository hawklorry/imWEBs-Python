
from typing import Any
from sqlalchemy import Column, TEXT, REAL, INTEGER
from .bmp_table import BMPTable


class PointSource(BMPTable):
    __tablename__ = 'point_source'
    ID = Column(INTEGER, primary_key=True)
    XLL = Column(REAL)
    YLL = Column(REAL)
    OPERATION = Column(TEXT)
    TABLENAME = Column(TEXT)

    def __init__(self):
        self.XLL = 0
        self.YLL = 0
        self.OPERATION = "1900-01-01"
        self.TABLENAME = ""

