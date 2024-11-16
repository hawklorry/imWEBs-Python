from ...delineation.structure_attribute import StructureAttribute

class Dugout:
    """Parameter Table for BMP: Dugout (38)"""

    def __init__(self, attribute:StructureAttribute = None):
        self.Scenario = -1
        """Dugout ID, obtained from dugout input data"""
        self.ID = attribute.id
        """Dugout type, 0 – filled with runoff, 1 – connected to a water course"""
        self.Type = 0
        """Operation starting year (designed for setting up dugout scenarios)"""
        self.Year = 0
        """Subbasin number, obtained from the watershed delineation"""
        self.Subbasin = attribute.subbasin 
        """Length of dugout when filled (m)"""
        self.MaxL_m = 100
        """Width of dugout when filled (m)"""
        self.MaxW_m = 50
        """Dugout depth when filled (m)"""
        self.MaxD_m = 10
        """Dugout side slope (-)"""
        self.SideSlope = 1.5
        """Dugout end slope (-)"""
        self.EndSlope = 4
        """Dugout volume capacity (104m3), calculated from above 4 parameters"""
        self.MaxVolume_104M3 = 0
        """Dugout drainage area (ha), obtained from dugout drainage area distribution"""
        self.Drainage_Area = attribute.contribution_area
        """Animal ID"""
        self.AniID = 2
        """Adult animal number"""
        self.AniAdult = 20
        """Non-adult animal number"""
        self.AniNonAdult = 20
        """Normal (equilibrium) sediment concentration in wetland (mg/l)"""
        self.NSED = 5
        """Sediment settling decay constant (1/day)"""
        self.Dcc = 0.184
        """Median partical size"""
        self.D50 = 10
        """Phosphorous settling rate in catch basin (m/year)"""
        self.SettVolP_mYr = 10
        """Nitrogen settling rate in catch basin (m/year)"""
        self.SettVolN_mYr = 10
        """Hydraulic conductivity of catch basin bottom (mm/hr)"""
        self.K_mmHr = 0.05
        """Chlorophyll production coefficient of catch basin"""
        self.CHLAR = 1
        """Water clarity coefficient of catch basin (m)"""
        self.SECCIR = 1
        """Initial water volume in catch basin (% of capacity),"""
        self.InitialVolume = 100
        """Initial sediment concentration in catch basin (mg/l)"""
        self.InitialSediment_mgL = 5
        """Initial concentration of NO3-N in catch basin (mg/l)"""
        self.InitialNO3_mgL = 0.5
        """Initial concentration of soluble P in catch basin (mg/l)"""
        self.InitialSolP_mgL = 0.05
        """Initial concentration of organic N in catch basin (mg/l)"""
        self.InitialOrgN_mgL = 0.5
        """Initial concentration of organic P in catch basin (mg/l)"""
        self.InitialOrgP_mgL = 0.05
