from .bmp_management_base import BMPManagementBase

class ManureApplicationBasedOnSoliNitrogenLimitManagement(BMPManagementBase):
    """Distribution Table for BMP: Application based on soil nitrogen limit (26)"""
    def __init__(self):
        super().__init__()
        self.NO3_N_Limit_kg_ha = 0
