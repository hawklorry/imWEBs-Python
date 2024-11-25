from typing import Any
from sqlalchemy import Column, TEXT, REAL, INTEGER
from .bmp_table import BMPTable
from ...names import Names
from whitebox_workflows import Vector, Raster


class SubArea(BMPTable):
    __tablename__ = Names.bmp_table_name_subarea

    Id = Column(INTEGER, primary_key=True)
    SubbasinId = Column(INTEGER)
    FieldId = Column(INTEGER)
    Area = Column(REAL)
    Elevation = Column(REAL)
    Slope = Column(REAL)
    USLE_P = Column(REAL)
    MoistureInitial = Column(REAL)
    FlowAccumulationAverage = Column(REAL)
    WetlandFraction = Column(REAL)
    TravelTimeAverage2 = Column(REAL)
    TravelTimeAverage10 = Column(REAL)
    TravelTimeAverage100 = Column(REAL)
    TravelTimeStd2 = Column(REAL)
    TravelTimeStd10 = Column(REAL)
    TravelTimeStd100 = Column(REAL)
    TopographyWeight = Column(REAL)
    LateralWidth = Column(REAL)
