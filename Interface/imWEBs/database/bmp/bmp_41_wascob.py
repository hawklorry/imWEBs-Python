from ...delineation.structure_attribute import StructureAttribute

class Wascob:
    """Parameter Table for BMP: WASCob (41)"""
    def __init__(self,attribute:StructureAttribute = None):
        self.Scenario = -1
        self.ID = attribute.id

        self.StartYear = 1900
        self.StartMon = 1
        self.StartDay = 1

        self.FieldId = -1
        self.OutletReachId = -1
        
        self.BermElevation = 0

        self.DeadVolume = 0
        self.DeadArea = 0

        self.NormalVolume = 0
        self.NormalArea = 0

        self.MaxVolume = 0
        self.MaxArea = 0

        self.ContributionArea = attribute.contribution_area
        self.DischargeCapacity = 0

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

        self.BermType = ''
