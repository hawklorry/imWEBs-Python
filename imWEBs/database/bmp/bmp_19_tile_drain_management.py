from ...bmp.bmp_type import DefaultScenarioId
from sqlalchemy import INT, REAL

class TileDrainParameter:
    """Parameter Table for BMP: till drainge management (19)"""

    def __init__(self, id:int, field_id:int, outlet_reach_id:int, 
                 depth:float, spacing:float, 
                 elevation:float, outlet_capacity:float):
        self.Scenario = DefaultScenarioId
        self.Id = id
        self.StartYear = 1970
        self.StartMon = 1
        self.StartDay = 1
        self.FieldId = field_id                 #field id
        self.OutletReachId = outlet_reach_id    #subbasin id,Assign tile-drain outlet of each tile drain field to the lower subbasin (reach). 
        self.Type = 0
        self.Elevation = elevation              #sum(Subarea.Area * Fraction * Subarea.Elevation) / sum(Subarea.Area * Fraction)
        self.Depth = depth                      #shapefile, depth from surface to tile-drain,mm
        self.ControlDepth = 500
        self.ControlStartMon = 4
        self.ControlEndMon = 10
        self.Radius = 50                        #mm
        self.Spacing = spacing                  #shapefile,mm
        self.OutletCapacity = outlet_capacity   #m3/day, assuming 10 mm rain on tile drain area
                                                #CAST(round(sum(sa.Area * lookup.FractionToSubarea) * 10 * 10 /* 30mm -> m3/day */, 2) AS REAL) 
                                                #Drainage capacity = 10 mm * tile drain field area (ha)
        self.LagCoefficient = 0.9
        self.DepthToImperviableLayer = 1500
        self.LateralKScale = 1.0
        self.SedimentCon = 100
        self.OrgNConc = 10
        self.OrgPConc = 10
        self.PRCTile = 0.75
        self.CNTile = 0.75
        self.GWT0 = 300

    @staticmethod 
    def column_types()->dict:
        tile_drain = TileDrainParameter(-1,-1,-1,-1,-1,-1,-1)
        return {col:(INT if col in ["Scenario","ID", "StartYear","StartMon","StartDay","FieldId","OutletReachId","Type","ControlStartMon","ControlEndMon"] else REAL) for col in dir(tile_drain) if "__" not in col}

