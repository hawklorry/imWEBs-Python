from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable

class CropManagement(BMPTable):    
    """Distribution Table for BMP: Crop management (12)"""
    __tablename__ = 'crop_management'
    Scenario = Column(Integer)
    Location = Column(Integer)
    ID = Column(Integer)
    Year = Column(Integer)
    ActualYear = Column(Integer)
    CropCode = Column(Integer)
    PlantingMon = Column(Integer)
    PlantingDay = Column(Integer)
    HarvestMon = Column(Integer)
    HarvestDay = Column(Integer)
    HarvestType = Column(Integer)
    HarvestEfficiency = Column(REAL)
    HarvestIndexOverride = Column(REAL)
    StoverFraction = Column(REAL)
    CNOP = Column(REAL)
    IsGrain = Column(Integer)
    PRCOP = Column(REAL)
        
    def __init__(self):
        """
        some default values
        """
        self.Year = 1
        self.HarvestType = 2
        self.HarvestEfficiency = 1
        self.HarvestIndexOverride = 0
        self.StoverFraction = 0
        self.CNOP = 1
        self.IsGrain = 1
        self.PRCOP = 1

    @staticmethod
    def default_crop_management():
        """
        get default crop management for crop 1-36
        """
        default_crop_rotation = {}

        default_crop_rotation[1] = CropManagement(CropCode=1,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[2] = CropManagement(CropCode=2,PlantingMon=5,PlantingDay=4,HarvestMon=8,HarvestDay=18)
        default_crop_rotation[3] = CropManagement(CropCode=3,PlantingMon=5,PlantingDay=25,HarvestMon=9,HarvestDay=14)
        default_crop_rotation[4] = CropManagement(CropCode=4,PlantingMon=6,PlantingDay=4,HarvestMon=10,HarvestDay=11)
        default_crop_rotation[5] = CropManagement(CropCode=5,PlantingMon=5,PlantingDay=18,HarvestMon=9,HarvestDay=11)
        default_crop_rotation[6] = CropManagement(CropCode=6,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[7] = CropManagement(CropCode=7,PlantingMon=5,PlantingDay=1,HarvestMon=8,HarvestDay=18)
        default_crop_rotation[8] = CropManagement(CropCode=8,PlantingMon=5,PlantingDay=21,HarvestMon=10,HarvestDay=25)
        default_crop_rotation[9] = CropManagement(CropCode=9,PlantingMon=4,PlantingDay=25,HarvestMon=10,HarvestDay=18)
        default_crop_rotation[10] = CropManagement(CropCode=10,PlantingMon=5,PlantingDay=4,HarvestMon=10,HarvestDay=4)
        default_crop_rotation[11] = CropManagement(CropCode=11,PlantingMon=9,PlantingDay=4,HarvestMon=8,HarvestDay=11)
        default_crop_rotation[12] = CropManagement(CropCode=12,PlantingMon=5,PlantingDay=11,HarvestMon=10,HarvestDay=11)
        default_crop_rotation[13] = CropManagement(CropCode=13,PlantingMon=5,PlantingDay=1,HarvestMon=8,HarvestDay=4)
        default_crop_rotation[14] = CropManagement(CropCode=14,PlantingMon=5,PlantingDay=25,HarvestMon=9,HarvestDay=18)
        default_crop_rotation[15] = CropManagement(CropCode=15,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[16] = CropManagement(CropCode=16,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[17] = CropManagement(CropCode=17,PlantingMon=5,PlantingDay=25,HarvestMon=8,HarvestDay=11)
        default_crop_rotation[18] = CropManagement(CropCode=18,PlantingMon=6,PlantingDay=18,HarvestMon=9,HarvestDay=4)
        default_crop_rotation[19] = CropManagement(CropCode=19,PlantingMon=6,PlantingDay=11,HarvestMon=8,HarvestDay=25)
        default_crop_rotation[20] = CropManagement(CropCode=20,PlantingMon=5,PlantingDay=25,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[21] = CropManagement(CropCode=21,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[22] = CropManagement(CropCode=22,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[23] = CropManagement(CropCode=23,PlantingMon=5,PlantingDay=14,HarvestMon=9,HarvestDay=6)
        default_crop_rotation[24] = CropManagement(CropCode=24,PlantingMon=5,PlantingDay=25,HarvestMon=7,HarvestDay=25)
        default_crop_rotation[25] = CropManagement(CropCode=25,PlantingMon=5,PlantingDay=11,HarvestMon=9,HarvestDay=25)
        default_crop_rotation[26] = CropManagement(CropCode=26,PlantingMon=5,PlantingDay=18,HarvestMon=9,HarvestDay=18)
        default_crop_rotation[27] = CropManagement(CropCode=27,PlantingMon=5,PlantingDay=1,HarvestMon=10,HarvestDay=1)
        default_crop_rotation[28] = CropManagement(CropCode=28,PlantingMon=5,PlantingDay=18,HarvestMon=9,HarvestDay=25)
        default_crop_rotation[29] = CropManagement(CropCode=29,PlantingMon=5,PlantingDay=11,HarvestMon=8,HarvestDay=18)
        default_crop_rotation[30] = CropManagement(CropCode=30,PlantingMon=6,PlantingDay=4,HarvestMon=9,HarvestDay=14)
        default_crop_rotation[31] = CropManagement(CropCode=31,PlantingMon=5,PlantingDay=18,HarvestMon=9,HarvestDay=11)
        default_crop_rotation[32] = CropManagement(CropCode=32,PlantingMon=5,PlantingDay=11,HarvestMon=10,HarvestDay=11)
        default_crop_rotation[33] = CropManagement(CropCode=33,PlantingMon=5,PlantingDay=11,HarvestMon=9,HarvestDay=25)
        default_crop_rotation[34] = CropManagement(CropCode=34,PlantingMon=5,PlantingDay=11,HarvestMon=9,HarvestDay=11)
        default_crop_rotation[35] = CropManagement(CropCode=35,PlantingMon=5,PlantingDay=11,HarvestMon=8,HarvestDay=18)
        default_crop_rotation[36] = CropManagement(CropCode=36,PlantingMon=9,PlantingDay=4,HarvestMon=8,HarvestDay=11)


        return default_crop_rotation

class CropParameter(BMPTable):
    """Parameter Table for BMP: Pasture crop management (34)"""
    __tablename__ = 'crop_parameter'
    ICNUM = Column(Integer, primary_key=True)
    CPNM = Column(REAL)
    DESCRIPTION = Column(REAL)
    IDC = Column(REAL)
    BIO_E = Column(REAL)
    HVSTI = Column(REAL)
    BLAI = Column(REAL)
    FRGRW1 = Column(REAL)
    LAIMX1 = Column(REAL)
    FRGRW2 = Column(REAL)
    LAIMX2 = Column(REAL)
    DLAI = Column(REAL)
    CHTMX = Column(REAL)
    RDMX = Column(REAL)
    T_OPT = Column(REAL)
    T_BASE = Column(REAL)
    CNYLD = Column(REAL)
    CPYLD = Column(REAL)
    BN1 = Column(REAL)
    BN2 = Column(REAL)
    BN3 = Column(REAL)
    BP1 = Column(REAL)
    BP2 = Column(REAL)
    BP3 = Column(REAL)
    WSYF = Column(REAL)
    USLE_C = Column(REAL)
    GSI = Column(REAL)
    VPDFR = Column(REAL)
    FRGMAX = Column(REAL)
    WAVP = Column(REAL)
    CO2HI = Column(REAL)
    BIOEHI = Column(REAL)
    RSDCO_PL = Column(REAL)
    OV_N = Column(REAL)
    CN2A = Column(REAL)
    CN2B = Column(REAL)
    CN2C = Column(REAL)
    CN2D = Column(REAL)
    FERTFIELD = Column(REAL)
    ALAI_MIN = Column(REAL)
    BIO_LEAF = Column(REAL)
    PHU = Column(REAL)
    CNOP = Column(REAL)
    LAI_INIT = Column(REAL)
    BIO_INIT = Column(REAL)
    CURYR_INIT = Column(REAL)

    def __init__(self):
        self.PHU = 1500
        self.CNOP = 1
        self.LAI_INIT = 0.1
        self.BIO_INIT = 10
        self.CURYR_INIT = 10
