from ...bmp.bmp_type import DefaultScenarioId
from sqlalchemy import INT, REAL

class TileDrainParameter:
    """Parameter Table for BMP: till drainge management (19)"""

    def __init__(self, 
                 id:int, 
                 field_id:int, 
                 outlet_reach_id:int, 
                 elevation:float,
                 depth:float = 900, 
                 spacing:float = 10000,                  
                 radius:float = 50,
                 start_year:int = 1900,
                 start_month:int = 1,
                 start_day:int = 1):
        self.Scenario = DefaultScenarioId
        self.Id = id
        self.StartYear = start_year
        self.StartMon = start_month
        self.StartDay = start_day
        self.FieldId = field_id                 #field id
        self.OutletReachId = outlet_reach_id    #subbasin id,Assign tile-drain outlet of each tile drain field to the lower subbasin (reach). 
        
        self.Elevation = elevation              #sum(Subarea.Area * Fraction * Subarea.Elevation) / sum(Subarea.Area * Fraction)
        self.Depth = depth                      #shapefile, depth from surface to tile-drain,mm
        self.Radius = radius                    #shapefile,mm
        self.Spacing = spacing                  #shapefile,mm

        self.Type = 0
        self.ControlDepth = 500
        self.ControlStartMon = 5
        self.ControlEndMon = 10
        self.OutletCapacity = 500               #m3/day
        self.LagCoefficient = 0.9
        self.DepthToImperviableLayer = 1500
        self.LateralKScale = 1.0
        self.SedimentCoef = 100
        self.OrgNCoef = 0.008
        self.OrgPCoef = 0.0016
        self.PRCTile = 0.75
        self.CNTile = 0.75
        self.GWT0 = 1000
        self.gw0 = 1000
        self.kg = 0.0035
        self.base_ex = 1.1
        self.gwmax = 500

    @staticmethod 
    def column_types()->dict:
        tile_drain = TileDrainParameter(-1,-1,-1,-1)
        return {col:(INT if col in ["Scenario","ID", "StartYear","StartMon","StartDay","FieldId","OutletReachId","Type","ControlStartMon","ControlEndMon"] else REAL) for col in dir(tile_drain) if "__" not in col}

