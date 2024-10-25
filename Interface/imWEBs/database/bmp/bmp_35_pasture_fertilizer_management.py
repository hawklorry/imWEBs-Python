from .bmp_15_fertilizer_management import FertlizerManagement

class PastureFertilizerManagement(FertlizerManagement):
    """Distribution Table for BMP: Pasture fertilizer management (35)"""
    def __init__(self, FerMon, FerDay, FerType, FerRate):
        super().__init__(FerMon, FerDay, FerType, FerRate)