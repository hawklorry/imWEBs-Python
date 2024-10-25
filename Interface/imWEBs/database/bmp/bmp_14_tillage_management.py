
from .bmp_management_base import BMPManagementBaseWithYear
from sqlalchemy import Column, Integer, REAL, TEXT
from .bmp_table import BMPTable
from ...names import Names

class TillageManagement(BMPManagementBaseWithYear):
    """Distribution Table for BMP: Tillage management (14)"""

    def __init__(self, TillMon:int,TillDay:int,TillCode:int):
        super().__init__()
        self.TillMon = TillMon
        self.TillDay = TillDay
        self.TillCode = TillCode  


    @staticmethod
    def default_tillage_management():
        default_tillage_for_crops = {}

        default_tillage_for_crops[1] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[2] =[TillageManagement(TillMon = 5,TillDay = 2,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)],
        default_tillage_for_crops[3] =[TillageManagement(TillMon = 5,TillDay = 23,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 26,TillCode = 106)
                ,TillageManagement(TillMon = 9,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 9,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[4] =[TillageManagement(TillMon = 6,TillDay = 2,TillCode = 86)
                ,TillageManagement(TillMon = 6,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 28,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[5] =[TillageManagement(TillMon = 5,TillDay = 16,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 19,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)],
        default_tillage_for_crops[6] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 24,TillCode = 108)],
        default_tillage_for_crops[7] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 9,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[8] =[TillageManagement(TillMon = 5,TillDay = 21,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 23,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[9] =[TillageManagement(TillMon = 4,TillDay = 23,TillCode = 86)
                ,TillageManagement(TillMon = 4,TillDay = 26,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 9,TillDay = 25,TillCode = 16)],
        default_tillage_for_crops[10] =[TillageManagement(TillMon = 5,TillDay = 2,TillCode = 106)
                ,TillageManagement(TillMon = 5,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 9,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[11] =[TillageManagement(TillMon = 9,TillDay = 9,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 13,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 3,TillCode = 108)],
        default_tillage_for_crops[12] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)],
        default_tillage_for_crops[13] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 8,TillDay = 14,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 4,TillCode = 108)],
        default_tillage_for_crops[14] =[TillageManagement(TillMon = 5,TillDay = 23,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 26,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 28,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[15] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[16] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[17] =[TillageManagement(TillMon = 5,TillDay = 25,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 25,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[18] =[TillageManagement(TillMon = 6,TillDay = 16,TillCode = 86)
                ,TillageManagement(TillMon = 6,TillDay = 19,TillCode = 106)
                ,TillageManagement(TillMon = 8,TillDay = 14,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 4,TillCode = 108)],
        default_tillage_for_crops[19] =[TillageManagement(TillMon = 6,TillDay = 9,TillCode = 108)
                ,TillageManagement(TillMon = 6,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[20] =[TillageManagement(TillMon = 5,TillDay = 23,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 26,TillCode = 106)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[21] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[22] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[23] =[TillageManagement(TillMon = 5,TillDay = 14,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 16,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 15,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 3,TillCode = 108)],
        default_tillage_for_crops[24] =[TillageManagement(TillMon = 5,TillDay = 23,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 26,TillCode = 106)
                ,TillageManagement(TillMon = 9,TillDay = 1,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 8,TillCode = 108)],
        default_tillage_for_crops[25] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 106)
                ,TillageManagement(TillMon = 9,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 19,TillCode = 108)],
        default_tillage_for_crops[26] =[TillageManagement(TillMon = 5,TillDay = 16,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 19,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 28,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[27] =[TillageManagement(TillMon = 4,TillDay = 29,TillCode = 108)
                ,TillageManagement(TillMon = 5,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 11,TillDay = 1,TillCode = 108)],
        default_tillage_for_crops[28] =[TillageManagement(TillMon = 5,TillDay = 16,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 19,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)],
        default_tillage_for_crops[29] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 106)
                ,TillageManagement(TillMon = 8,TillDay = 28,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[30] =[TillageManagement(TillMon = 6,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 6,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[31] =[TillageManagement(TillMon = 5,TillDay = 16,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 19,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)],
        default_tillage_for_crops[32] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 10,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[33] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 106)
                ,TillageManagement(TillMon = 10,TillDay = 5,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 25,TillCode = 108)],
        default_tillage_for_crops[34] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 28,TillCode = 89)
                ,TillageManagement(TillMon = 10,TillDay = 18,TillCode = 108)],
        default_tillage_for_crops[35] =[TillageManagement(TillMon = 5,TillDay = 9,TillCode = 86)
                ,TillageManagement(TillMon = 5,TillDay = 12,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 14,TillCode = 106)
                ,TillageManagement(TillMon = 10,TillDay = 4,TillCode = 89)],
        default_tillage_for_crops[36] =[TillageManagement(TillMon = 9,TillDay = 2,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 5,TillCode = 108)
                ,TillageManagement(TillMon = 9,TillDay = 21,TillCode = 106)
                ,TillageManagement(TillMon = 10,TillDay = 11,TillCode = 108)]

class TillageParameter(BMPTable):
    """Parameter Table for BMP: Pasture tillage management (36)"""
    __tablename__ = Names.bmp_table_name_tillage_parameter
    ITNUM = Column(Integer, primary_key=True)
    TILLNM = Column(TEXT)
    DESCRIPTION = Column(TEXT)
    EFFMIX = Column(REAL)
    DEPTIL = Column(REAL)
    CNOP_CN2 = Column(REAL)
    PRC = Column(REAL)
    DSC = Column(REAL)
