
from .bmp_management_base import BMPManagementBaseWithYear

class GrazingManagement(BMPManagementBaseWithYear):
    """Distribution Table for BMP: Grazing management (16)"""

    def __init__(self):
        super().__init__()
        """BMP start month"""
        self.GraMon = 9
        """BMP start day"""
        self.GraDay = 1
        """BMP lasting days"""
        self.Days = 45
        """Animal ID"""
        self.Ani_ID = 1
        """Adult animal percentage"""
        self.Ani_adult = 50
        """Grazing density (1/ha)"""
        self.GR_Density = 15
        """Fraction of day animal stay in field"""
        self.DayFra = 0.3
        """Water source type, 0 - outside watershed e.g. deep groundwater, 1 - reach, 2 - reservoir, 3 - catch basin, 4 - groundwater, 5 - wetland, 6 - dugout"""
        self.Source = 1
        """Water source ID"""
        self.SourceID = 0
        """Dugout IDs in the grazing area"""
        self.Dugout_ID = 0
        """0 – accessible, 1 – managed access, 2 – no access"""
        self.Access = 0
        """0 – no fencing, 1- fencing"""
        self.Fencing = 0
        """Percent of animals drinking in streams. Default is 1"""
        self.StreamAniPerc = 1
        """Percent of day time for drinking, default is 0.02 (0.5/24)"""
        self.Drinking_time = 0.02
        """Average bank erodibility change compared to no-fencing """
        self.BankK_Change = 0.3
