from typing import Any
from sqlalchemy import Column, Integer, Float, TEXT, REAL, TEXT
from .bmp_table import BMPTable
from ...delineation.structure_attribute import StructureAttribute
import math
from ...names import Names

class Wetland(BMPTable):
    """Parameter Table for BMP: Isolated wetland (9)"""
    __tablename__ = Names.bmp_table_name_wetland
    ID = Column(TEXT, primary_key=True)
    OperationYear = Column(Integer)
    Subbasin = Column(Integer)
    Type = Column(TEXT)
    ContributionArea_ha = Column(REAL)
    NormalArea_ha = Column(REAL)
    NormalVolume_104M3 = Column(REAL)
    MaxArea_ha = Column(REAL)
    MaxVolume_104M3 = Column(REAL)
    K_mmHr = Column(REAL)
    SedimentConEqui_mgL = Column(REAL)
    D50_um = Column(REAL)
    SettVolN_mYr = Column(REAL)
    SettVolP_mYr = Column(REAL)
    ChlaProCo = Column(REAL)
    WaterCalCo = Column(REAL)
    InflowFrac = Column(REAL)
    InitialVolume_104M3 = Column(REAL)
    InitialSediment_mgL = Column(REAL)
    InitialNO3_mgL = Column(REAL)
    InitialNO2_mgL = Column(REAL)
    InitialNH3_mgL = Column(REAL)
    InitialSolP_mgL = Column(REAL)
    InitialOrgN_mgL = Column(REAL)
    InitialOrgP_mgL = Column(REAL)
    RoutingConstant = Column(REAL)
    ClassType = Column(TEXT)

    #use fixed for now
    #read from parameter database later
    co1 = 2.85
    ex1 = 1.22
    co2 = 7.1
    cons = 9.97
    Ivol = 100

    def __init__(self, attribute:StructureAttribute = None):
        if attribute is not None:
            self.ID = attribute.id
            self.ContributionArea_ha = attribute.contribution_area
            self.Subbasin = attribute.subbasin
            self.MaxArea_ha = attribute.area_ha            

            #use the surface area to calculate the volume
            if attribute.area_ha < 70:
                self.MaxVolume_104M3 = self.co1 * math.pow(self.MaxArea_ha, self.ex1) / 10.0
            else:
                self.MaxVolume_104M3 = (self.co2 * self.MaxArea_ha + self.cons) / 10.0

            #set to the same for now
            self.NormalArea_ha = self.MaxArea_ha
            self.NormalVolume_104M3 = self.MaxVolume_104M3

            #initial volume
            self.InitialVolume_104M3 = self.NormalVolume_104M3 * self.Ivol / 100
        else:
            self.ContributionArea_ha = 0
            self.NormalArea_ha = 0
            self.NormalVolume_104M3 = 0
            self.MaxArea_ha = 0
            self.MaxVolume_104M3 = 0
            self.InitialVolume_104M3 = 0
                
        #all wetland is operational
        self.OperationYear = 0
        self.Type = "Isolated"
        
        #these parameters has default values from parameter databaase, wetland table
        self.K_mmHr = 0.05
        self.SedimentConEqui_mgL = 5
        self.D50_um = 10
        self.SettVolN_mYr = 10
        self.SettVolP_mYr = 10
        self.ChlaProCo = 1
        self.WaterCalCo = 1
        self.InflowFrac = 1        
        self.InitialSediment_mgL = 5
        self.InitialNO3_mgL = 0.5
        self.InitialNO2_mgL = 0.1
        self.InitialNH3_mgL = 0.1
        self.InitialSolP_mgL = 0.05
        self.InitialOrgN_mgL = 0.5
        self.InitialOrgP_mgL = 0.05
        self.RoutingConstant = 10