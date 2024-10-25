from .bmp_management_base import BMPManagementBase

class ManureApplicationBasedOnPhosphorousLimitManagement(BMPManagementBase):
    """Distribution Table for BMP: Application based on soil Phosphorous limit (25)"""
    def __init__(self):
        super().__init__()
        self.Soil_P_Limit_kg_ha = 0
