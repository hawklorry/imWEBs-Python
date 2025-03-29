from sqlalchemy import INT, TEXT, REAL

class VegetationFilterStrip:
    """Distribution Table for BMP: RVegetation Filter Strip (7)"""

    def __init__(self):
        """Scenario ID"""
        self.Scenario = -1
        """filter strip drainage part id used for IMWEBs model calculation, one RIBUF may contain several drainage parts"""
        self.ID = -1
        """Year of operation"""
        self.Year = 1
        """Group filter strip ID"""
        self.VFST_ID = 0
        """Subbasin ID"""
        self.Subbasin = 0
        """Vegetation ID"""
        self.VegetationID = 6
        """Length of the filter strip (m)"""
        self.Length = 0
        """Width of the filter strip (m)"""
        self.Width = 0
        """Area of the filter strip (ha)"""
        self.Area_ha = 0
        """Drainage area (ha)"""
        self.Drainage_Area = 0
        """filter strip drainage area to filter strip area ratio"""
        self.Area_Ratio = 0
        """Slope of the filter strip (%)"""
        self.Slope = 0
        """filter strip soil saturation hydraulic conductivity (mm/hr)"""
        self.Sol_K = 0.25
        """filter strip soil porosity"""
        self.Sol_porosity = 0
        """filter strip root depth (mm)"""
        self.Root_Depth = 0

    @staticmethod 
    def column_types()->dict:
        filter_strip = VegetationFilterStrip()
        return {col:(INT if col in ["Scenario","ID", "Year","VFST_ID","Subbasin","VegetationID"] else REAL) for col in dir(filter_strip) if "__" not in col}

if __name__ == "__main__":
    col_types = VegetationFilterStrip.column_types()
    print(len(col_types))
