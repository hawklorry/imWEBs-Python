from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from .bmp_management_base import BMPManagementBaseWithYear
from ...names import Names

class FertlizerManagement(BMPManagementBaseWithYear):
    """Distribution Table for BMP: Fertilizer management (15)"""

    def __init__(self,FerMon:int,FerDay:int,FerType:int,FerRate:int):
        super().__init__()
        self.FerMon = FerMon
        self.FerDay = FerDay
        self.FerType = FerType
        self.FerRate = FerRate
        self.FerSurface = 0.2

    @staticmethod
    def default_fertilizer_management():
        """
        get default fertilizer management for crop 1-36
        """
        default_fertilizer_fro_crops = {}

        default_fertilizer_fro_crops[1] =[FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 57)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 20)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 90)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 12)],
        default_fertilizer_fro_crops[2] =[FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 1,FerRate = 19)
                ,FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 75)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 13)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 77)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 99)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 10)],
        default_fertilizer_fro_crops[3] =[FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 22)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 75)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 14)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 64)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 56)],
        default_fertilizer_fro_crops[4] =[FertlizerManagement(FerMon = 6,FerDay = 4,FerType = 1,FerRate = 17)
                ,FertlizerManagement(FerMon = 6,FerDay = 4,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 50)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 10)
                ,FertlizerManagement(FerMon = 7,FerDay = 25,FerType = 1,FerRate = 39)
                ,FertlizerManagement(FerMon = 7,FerDay = 25,FerType = 2,FerRate = 9)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 77)],
        default_fertilizer_fro_crops[5] =[FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 1,FerRate = 24)
                ,FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 95)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 14)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 89)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 91)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 10)],
        default_fertilizer_fro_crops[6] =[FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 1,FerRate = 106)
                ,FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 2,FerRate = 15)],
        default_fertilizer_fro_crops[7] =[FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 1,FerRate = 106)
                ,FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 78)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 15)],
        default_fertilizer_fro_crops[8] =[FertlizerManagement(FerMon = 5,FerDay = 21,FerType = 1,FerRate = 17)
                ,FertlizerManagement(FerMon = 5,FerDay = 21,FerType = 2,FerRate = 13)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 85)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 10)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 1,FerRate = 92)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 2,FerRate = 10)],
        default_fertilizer_fro_crops[9] =[FertlizerManagement(FerMon = 4,FerDay = 18,FerType = 1,FerRate = 91)
                ,FertlizerManagement(FerMon = 4,FerDay = 18,FerType = 2,FerRate = 20)
                ,FertlizerManagement(FerMon = 4,FerDay = 25,FerType = 1,FerRate = 11)
                ,FertlizerManagement(FerMon = 4,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 112)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 90)],
        default_fertilizer_fro_crops[11] =[FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 1,FerRate = 57)
                ,FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 2,FerRate = 20)
                ,FertlizerManagement(FerMon = 9,FerDay = 4,FerType = 1,FerRate = 19)
                ,FertlizerManagement(FerMon = 9,FerDay = 4,FerType = 2,FerRate = 10)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 101)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 7)],
        default_fertilizer_fro_crops[12] =[FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 56)],
        default_fertilizer_fro_crops[13] =[FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 90)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 12)],
        default_fertilizer_fro_crops[14] =[FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 20)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 65)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 64)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 73)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 10)],
        default_fertilizer_fro_crops[15] =[FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 1,FerRate = 40)
                ,FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 55)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 16)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 1,FerRate = 63)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 59)],
        default_fertilizer_fro_crops[16] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 73)],
        default_fertilizer_fro_crops[17] =[FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 12)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 54)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 25)],
        default_fertilizer_fro_crops[18] =[FertlizerManagement(FerMon = 7,FerDay = 25,FerType = 1,FerRate = 76)],
        default_fertilizer_fro_crops[19] =[FertlizerManagement(FerMon = 6,FerDay = 11,FerType = 1,FerRate = 18)
                ,FertlizerManagement(FerMon = 6,FerDay = 11,FerType = 2,FerRate = 24)],
        default_fertilizer_fro_crops[20] =[FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 17)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 57)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 1,FerRate = 71)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 2,FerRate = 19)],
        default_fertilizer_fro_crops[21] =[FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 65)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 18)],
        default_fertilizer_fro_crops[23] =[FertlizerManagement(FerMon = 5,FerDay = 14,FerType = 1,FerRate = 6)
                ,FertlizerManagement(FerMon = 5,FerDay = 14,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 1,FerRate = 56)],
        default_fertilizer_fro_crops[24] =[FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 1,FerRate = 36)
                ,FertlizerManagement(FerMon = 5,FerDay = 25,FerType = 2,FerRate = 20)],
        default_fertilizer_fro_crops[25] =[FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 67)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 15)],
        default_fertilizer_fro_crops[26] =[FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 1,FerRate = 25)
                ,FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 2,FerRate = 13)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 68)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 58)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 80)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 11)],
        default_fertilizer_fro_crops[27] =[FertlizerManagement(FerMon = 5,FerDay = 1,FerType = 1,FerRate = 56)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 57)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 1,FerRate = 74)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 101)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 17)],
        default_fertilizer_fro_crops[28] =[FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 1,FerRate = 19)
                ,FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 1,FerRate = 15)
                ,FertlizerManagement(FerMon = 7,FerDay = 18,FerType = 2,FerRate = 20)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 78)],
        default_fertilizer_fro_crops[29] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 90)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 67)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 10)],
        default_fertilizer_fro_crops[30] =[FertlizerManagement(FerMon = 7,FerDay = 25,FerType = 1,FerRate = 56)
                ,FertlizerManagement(FerMon = 7,FerDay = 25,FerType = 2,FerRate = 20)],
        default_fertilizer_fro_crops[31] =[FertlizerManagement(FerMon = 5,FerDay = 18,FerType = 1,FerRate = 22)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 22)],
        default_fertilizer_fro_crops[32] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 54)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 77)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 7)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 10)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 112)],
        default_fertilizer_fro_crops[33] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 67)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 78)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 15)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 20)],
        default_fertilizer_fro_crops[34] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 21)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 1,FerRate = 79)
                ,FertlizerManagement(FerMon = 6,FerDay = 18,FerType = 2,FerRate = 14)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 1,FerRate = 75)
                ,FertlizerManagement(FerMon = 6,FerDay = 25,FerType = 2,FerRate = 12)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 82)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 14)],
        default_fertilizer_fro_crops[35] =[FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 1,FerRate = 6)
                ,FertlizerManagement(FerMon = 5,FerDay = 11,FerType = 2,FerRate = 17)
                ,FertlizerManagement(FerMon = 7,FerDay = 11,FerType = 1,FerRate = 118)],
        default_fertilizer_fro_crops[36] =[FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 1,FerRate = 97)
                ,FertlizerManagement(FerMon = 5,FerDay = 4,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 9,FerDay = 4,FerType = 1,FerRate = 7)
                ,FertlizerManagement(FerMon = 9,FerDay = 4,FerType = 2,FerRate = 11)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 1,FerRate = 35)
                ,FertlizerManagement(FerMon = 9,FerDay = 11,FerType = 2,FerRate = 6)]

        return default_fertilizer_fro_crops
    
class FertilizerParameter(BMPTable):
    __tablename__ = Names.bmp_table_name_fertilizer_parameter
    IFNUM = Column(Integer, primary_key=True)
    FERTNM = Column(TEXT)
    DESCRIPTION = Column(TEXT)
    FMINN = Column(REAL)
    FMINP = Column(REAL)
    FORGN = Column(REAL)
    FORGP = Column(REAL)
    FNH3N = Column(REAL)
    BACTPDB = Column(REAL)
    BACTLPDB = Column(REAL)
    BACKTKDDB = Column(REAL)
    IsManure = Column(Integer)