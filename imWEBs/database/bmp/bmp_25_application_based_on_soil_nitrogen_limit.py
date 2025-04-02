from .bmp_management_base import BMPManagementBase

class ManureApplicationBasedOnSoliNitrogenLimitManagement(BMPManagementBase):
    """Distribution Table for BMP: Application based on soil nitrogen limit (26)"""
    def __init__(self, location:int):
        super().__init__(location)
        self.NO3_N_Limit_kg_ha = 0
