from ...delineation.structure_attribute import StructureAttribute
from ...bmp.bmp_type import DefaultScenarioId
from sqlalchemy import INT, TEXT, REAL

class Wascob:
    """Parameter Table for BMP: WASCob (41)"""
    def __init__(self,
                 id:int, 
                 field_id:int,
                 subbasin_id:int, 
                 outlet_reach_id:int,
                 start_year:int = 1900, 
                 start_month:int = 1,
                 start_day:int = 1,
                 berm_elevation:float = 0, 
                 dead_volume:float = 0,
                 dead_area:float = 0,
                 normal_volumne:float = 0,
                 normal_area:float = 0,
                 max_volume:float = 0, 
                 max_area:float = 0, 
                 capacity:float = 0,
                 contribution_area:float = 0):
        
        self.Scenario = DefaultScenarioId
        self.ID = id 

        self.StartYear = start_year  
        self.StartMon = start_month
        self.StartDay = start_day

        self.FieldId = field_id                 #get from spatial
        self.SubbasinId = subbasin_id
        self.OutletReachId = outlet_reach_id    #wascob has an atribute for outlet id, if the outlet is set to 
                                                #outlet of subbasin, then outlet reach id will be the downstream reach id.

        self.BermElevation = berm_elevation  

        self.DeadVolume = dead_volume
        self.DeadArea = dead_area

        self.NormalVolume = normal_volumne 
        self.NormalArea = normal_area    

        self.MaxVolume = max_volume      #from shapefile
        self.MaxArea = max_area        #from shapefile

        self.ContributionArea = contribution_area
        self.DischargeCapacity = capacity  #from shapefile

        #below paramter use default values
        self.TileOutflowCoefficient = 1
        self.SpillwayDecay = 1

        self.K = 2.5
        self.Nsed = 1
        self.D50 = 10
        self.Dcc = 0.185

        self.PSettle = 10
        self.NSettle = 10
        self.Chlaw = 1
        self.Secciw = 1

        self.InitialVolume = 0
        self.InitialSedimentConc = 0

        self.InitialSolPConc = 0.05
        self.InitialOrgPConc = 0.05

        self.InitialNO3Conc = 0.5
        self.InitialOrgNConc = 0.5
        self.InitialNO2Conc = 0.1
        self.InitialNH3Conc = 0.1

    @staticmethod 
    def column_types()->dict:
        wascob = Wascob(-1,-1,-1,-1)
        return {col:(INT if col in ["Scenario","ID", "StartYear","StartMon","StartDay","FieldId","SubbasinId","OutletReachId"] else REAL) for col in dir(wascob) if "__" not in col}