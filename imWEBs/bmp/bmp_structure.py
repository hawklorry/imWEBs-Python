from .bmp import BMP
from whitebox_workflows import Vector, Raster
import pandas as pd

class StructureBMP(BMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster):
        super.__init__(bmp_vector, subbasin_raster)


