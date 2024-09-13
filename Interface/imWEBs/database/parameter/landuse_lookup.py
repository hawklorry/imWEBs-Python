from sqlalchemy import Column, Integer, Float, String
from .parameter_table import ParameterTable

class LanduseLookup(ParameterTable):
    __tablename__ = 'LanduseLookup'
    LANDUSE_ID = Column(Float, primary_key=True)
    CODE = Column(String)
    LANDUSE_NAME = Column(String)
    CN2A = Column(Float)
    CN2B = Column(Float)
    CN2C = Column(Float)
    CN2D = Column(Float)
    ROOT_DEPTH = Column(Float)
    MANNING = Column(Float)
    I_MAX = Column(Float)
    I_MIN = Column(Float)
    SHC = Column(Float)
    SOIL_T10 = Column(Float)
    USLE_C = Column(Float)
    PET_FR = Column(Float)
    PRC_ST1 = Column(Float)
    PRC_ST2 = Column(Float)
    PRC_ST3 = Column(Float)
    PRC_ST4 = Column(Float)
    PRC_ST5 = Column(Float)
    PRC_ST6 = Column(Float)
    PRC_ST7 = Column(Float)
    PRC_ST8 = Column(Float)
    PRC_ST9 = Column(Float)
    PRC_ST10 = Column(Float)
    PRC_ST11 = Column(Float)
    PRC_ST12 = Column(Float)
    SC_ST1 = Column(Float)
    SC_ST2 = Column(Float)
    SC_ST3 = Column(Float)
    SC_ST4 = Column(Float)
    SC_ST5 = Column(Float)
    SC_ST6 = Column(Float)
    SC_ST7 = Column(Float)
    SC_ST8 = Column(Float)
    SC_ST9 = Column(Float)
    SC_ST10 = Column(Float)
    SC_ST11 = Column(Float)
    SC_ST12 = Column(Float)
    DSC_ST1 = Column(Float)
    DSC_ST2 = Column(Float)
    DSC_ST3 = Column(Float)
    DSC_ST4 = Column(Float)
    DSC_ST5 = Column(Float)
    DSC_ST6 = Column(Float)
    DSC_ST7 = Column(Float)
    DSC_ST8 = Column(Float)
    DSC_ST9 = Column(Float)
    DSC_ST10 = Column(Float)
    DSC_ST11 = Column(Float)
    DSC_ST12 = Column(Float)
    FIMP = Column(Float)
    FCIMP = Column(Float)
    CURBDEN = Column(Float)
    URBCOEF = Column(Float)
    DIRTMX = Column(Float)
    THALF = Column(Float)
    TNCONC = Column(Float)
    TPCONC = Column(Float)
    TNO3CONC = Column(Float)
    URBCN2 = Column(Float)
    IS_AGRICULTURAL = Column(Float)
    IsTameGrass = Column(Float)

    @property
    def is_agricultrual(self):
        return getattr(self, "IS_AGRICULTURAL") > 0

    @property
    def field_capacity(self):
        return getattr(self, "FC1")
    
    def getPotentialRunoffCoefficient(self, soil_texture:int)->float:
        """Get potential runoff coefficient for given soil texture"""
        return getattr(self, f"PRC_ST{soil_texture}")

    def getDepressionStorageCapacity(self, soil_texture:int)->float:
        """Get depression storage capacity for given soil texture"""
        return getattr(self, f"DSC_ST{soil_texture}")

    def getSlope(self, soil_texture:int)->float:
        """Get slope for given soil texture"""
        return getattr(self, f"SC_ST{soil_texture}")

    def getCN2(self, hydrological_group)->float:
        """get CN2 for given soil hydrolgical group number 1,2,3,4 which could be read from soil lookup table HG column"""
        soil_classes = ["A", "B", "C", "D"]
        return getattr(self, f"CN2{soil_classes[int(hydrological_group - 1)]}")