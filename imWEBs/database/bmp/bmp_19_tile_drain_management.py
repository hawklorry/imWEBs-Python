class TileDrainParameter:
    """Parameter Table for BMP: till drainge management (19)"""

    def __init__(self):
        self.Scenario = -1
        self.Id = -1
        self.StartYear = 1900
        self.StartMon = 1
        self.StartDay = 1
        self.FieldId = -1
        self.OutletReachId = -1
        self.Type = 0
        self.Elevation = -1
        self.Depth = 914.4
        self.ControlDepth = 500
        self.ControlStartMon = 4
        self.ControlEndMon = 10
        self.Radius = 50
        self.Spacing = 12192
        self.OutletCapacity = 0
        self.LagCoefficient = 0.9
        self.DepthToImperviableLayer = 1500
        self.LateralKScale = 1
        self.SedimentCon = 100
        self.OrgNConc = 10
        self.OrgPConc = 10
        self.PRCTile = 0.75
        self.CNTile = 0.75
        self.GWT0 = 300

