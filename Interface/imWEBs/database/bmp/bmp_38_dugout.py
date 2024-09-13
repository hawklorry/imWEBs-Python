from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable

class DugoutParameter(BMPTable):
    """Parameter Table for BMP: Dugout (38)"""
    __tablename__ = 'dugout_parameter'

    """Scenario ID"""
    Scenario = Column(Integer)
    """Dugout ID, obtained from dugout input data"""
    ID = Column(Integer)
    """Dugout type, 0 – filled with runoff, 1 – connected to a water course"""
    Type = Column(Integer)
    """Operation starting year (designed for setting up dugout scenarios)"""
    Year = Column(Integer)
    """Subbasin number, obtained from the watershed delineation"""
    Subbasin = Column(Integer)
    """Length of dugout when filled (m)"""
    MaxL_m = Column(REAL)
    """Width of dugout when filled (m)"""
    MaxW_m = Column(REAL)
    """Dugout depth when filled (m)"""
    MaxD_m = Column(REAL)
    """Dugout side slope (-)"""
    SideSlope = Column(REAL)
    """Dugout end slope (-)"""
    EndSlope = Column(REAL)
    """Dugout volume capacity (104m3), calculated from above 4 parameters"""
    MaxVolume_104M3 = Column(REAL)
    """Dugout drainage area (ha), obtained from dugout drainage area distribution"""
    Drainage_Area = Column(REAL)
    """Animal ID"""
    AniID = Column(Integer)
    """Adult animal number"""
    AniAdult = Column(Integer)
    """Non-adult animal number"""
    AniNonAdult = Column(Integer)
    """Normal (equilibrium) sediment concentration in wetland (mg/l)"""
    NSED = Column(REAL)
    """Sediment settling decay constant (1/day)"""
    Dcc = Column(REAL)
    """Median partical size"""
    D50 = Column(REAL)
    """Phosphorous settling rate in catch basin (m/year)"""
    SettVolP_mYr = Column(REAL)
    """Nitrogen settling rate in catch basin (m/year)"""
    SettVolN_mYr = Column(REAL)
    """Hydraulic conductivity of catch basin bottom (mm/hr)"""
    K_mmHr = Column(REAL)
    """Chlorophyll production coefficient of catch basin"""
    CHLAR = Column(REAL)
    """Water clarity coefficient of catch basin (m)"""
    SECCIR = Column(REAL)
    """Initial water volume in catch basin (% of capacity),"""
    InitialVolume = Column(REAL)
    """Initial sediment concentration in catch basin (mg/l)"""
    InitialSediment_mgL = Column(REAL)
    """Initial concentration of NO3-N in catch basin (mg/l)"""
    InitialNO3_mgL = Column(REAL)
    """Initial concentration of soluble P in catch basin (mg/l)"""
    InitialSolP_mgL = Column(REAL)
    """Initial concentration of organic N in catch basin (mg/l)"""
    InitialOrgN_mgL = Column(REAL)
    """Initial concentration of organic P in catch basin (mg/l)"""
    InitialOrgP_mgL = Column(REAL)


    def __init__(self):
        self.Type = 0
        self.Year = 0
        self.MaxL_m = 100
        self.MaxW_m = 50
        self.MaxD_m = 10
        self.SideSlope = 1.5
        self.EndSlope = 4
        self.MaxVolume_104M3 = 0
        self.Drainage_Area = 0
        self.AniID = 2
        self.AniAdult = 20
        self.AniNonAdult = 20
        self.NSED = 5
        self.Dcc = 0.184
        self.D50 = 10
        self.SettVolP_mYr = 10
        self.SettVolN_mYr = 10
        self.K_mmHr = 0.05
        self.CHLAR = 1
        self.SECCIR = 1
        self.InitialVolume = 100
        self.InitialSediment_mgL = 5
        self.InitialNO3_mgL = 0.5
        self.InitialSolP_mgL = 0.05
        self.InitialOrgN_mgL = 0.5
        self.InitialOrgP_mgL = 0.05
