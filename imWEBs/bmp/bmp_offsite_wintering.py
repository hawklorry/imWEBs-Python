from .bmp import BMP
from whitebox_workflows import Vector, Raster
from .bmp_type import BMPType, ReachBMPColumnNames
from ..database.bmp.reach_bmp import ReachBMPDistribution 
import pandas as pd
from ..database.bmp.bmp_39_offsite_watering import OffsiteWateringParameter

class BMPOffsiteWintering(BMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster):
        super().__init__(bmp_vector, subbasin_raster)

    @property
    def offsite_wintering_parameters(self):
        return [OffsiteWateringParameter(id,sub) for id,sub in self.subbasins.items()]