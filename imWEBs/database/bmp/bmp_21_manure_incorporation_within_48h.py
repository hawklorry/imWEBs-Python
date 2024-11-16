from .bmp_management_base import BMPManagementBase

class ManureIncorporationWithin48hManagemet(BMPManagementBase):
    """Distribution Table for BMP: Manure incorporation with 48h (21)"""

    def __init__(self):
        super().__init__()
        self.FerSurface = 0.2

