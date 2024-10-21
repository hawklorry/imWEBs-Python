from .bmp import BMP
from whitebox_workflows import Vector, Raster
import pandas as pd
from ..delineation.structure import Structure
from ..database.bmp.bmp_41_wascob import Wascob

class StructureBMPWascob(BMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster, structure:Structure):
        super.__init__(bmp_vector, subbasin_raster)

        self.structure = structure

    @property
    def wascob_df(self)->pd.DataFrame:
        wascobs = [Wascob(att) for att in self.structure.attributes]
        return pd.DataFrame([vars(rb) for rb in wascobs])

