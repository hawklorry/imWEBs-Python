from .bmp_reach import ReachBMP
from whitebox_workflows import Vector, Raster
import pandas as pd

class ReachBMPWetland(ReachBMP):
    def __init__(self, wetland_vector:Vector, subbasin_raster:Raster):
        super().__init__(wetland_vector, subbasin_raster)
