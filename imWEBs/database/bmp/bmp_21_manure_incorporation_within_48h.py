from .bmp_management_base import BMPManagementBase

class ManureIncorporationWithin48hManagement(BMPManagementBase):
    """Distribution Table for BMP: Manure incorporation with 48h (21)"""

    def __init__(self, location:int):
        super().__init__(location)
        self.FerSurface = 0.2

