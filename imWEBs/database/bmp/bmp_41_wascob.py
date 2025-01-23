from ...delineation.structure_attribute import StructureAttribute
from ...bmp.bmp_type import DefaultScenarioId
from sqlalchemy import INT, TEXT, REAL

class Wascob:
    """Parameter Table for BMP: WASCob (41)"""
    def __init__(self,id:int, contribution_area:float, year:int, field_id:int, subbasin_id:int, outlet_reach_id:int, berm_elevation:float, max_volume:float, max_area:float, capacity:float):
        self.Scenario = DefaultScenarioId
        self.ID = id 

        self.StartYear = year   #from shapefile
        self.StartMon = 1
        self.StartDay = 1

        self.FieldId = field_id                 #get from spatial
        self.SubbasinId = subbasin_id
        self.OutletReachId = outlet_reach_id    #wascob has an atribute for outlet id, if the outlet is set to 
                                                #outlet of subbasin, then outlet reach id will be the downstream reach id.
        
		#BermElevation = avg(subarea with WASCoB elevation) + 2m (IF Height IS NULL)
        #BermElevation = avg(subarea with WASCOB elevation) + WASCoB.Height IF Height IS NOT NULL
        self.BermElevation = berm_elevation  

        self.DeadVolume = 0    
        self.DeadArea = 0      

        #normal volume = maxvolume *2 /3
        #normal area = max area / 1.31
        self.NormalVolume = max_volume * 2 / 3.0   
        self.NormalArea = max_area / 1.31     

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
        wascob = Wascob(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1)
        return {col:(INT if col in ["Scenario","ID", "StartYear","StartMon","StartDay","FieldId","SubbasinId","OutletReachId"] else REAL) for col in dir(wascob) if "__" not in col}