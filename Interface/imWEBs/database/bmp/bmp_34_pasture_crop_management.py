from .bmp_12_crop_management import CropManagement

class PastureCropManagement(CropManagement):
    def __init__(self, CropCode, PlantingMon, PlantingDay, HarvestMon, HarvestDay):
        super().__init__(CropCode, PlantingMon, PlantingDay, HarvestMon, HarvestDay)


