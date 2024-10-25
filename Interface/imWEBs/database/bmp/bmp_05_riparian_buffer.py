class RiparianBuffer:
    """Distribution Table for BMP: Riparian buffer (5)"""

    def __init__(self):
        """Scenario ID"""
        self.Scenario = -1
        """Riparian buffer drainage part id used for IMWEBs model calculation, one RIBUF may contain several drainage parts"""
        self.ID = -1
        """Year of operation"""
        self.Year = 1
        """Group riparian buffer ID"""
        self.RIBUF_ID = 0
        """Subbasin ID"""
        self.Subbasin = 0
        """Vegetation ID"""
        self.VegetationID = 6
        """Length of the riparian buffer (m)"""
        self.Length = 0
        """Width of the riparian buffer (m)"""
        self.Width = 0
        """Area of the riparian buffer (ha)"""
        self.Area_ha = 0
        """Drainage area (ha)"""
        self.Drainage_Area = 0
        """Riparian buffer drainage area to riparian buffer area ratio"""
        self.Area_Ratio = 0
        """Slope of the riparian buffer (%)"""
        self.Slope = 0
        """Riparian buffer soil saturation hydraulic conductivity (mm/hr)"""
        self.Sol_K = 0.25
        """Riparian buffer soil porosity"""
        self.Sol_porosity = 0
        """Riparian buffer root depth (mm)"""
        self.Root_Depth = 0
