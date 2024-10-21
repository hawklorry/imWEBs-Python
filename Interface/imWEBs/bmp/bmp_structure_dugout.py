from .bmp import BMP
from whitebox_workflows import Vector, Raster
import pandas as pd
from ..delineation.structure import Structure
from ..database.bmp.bmp_38_dugout import Dugout

class StructureBMPDugout(BMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster, structure:Structure):
        super.__init__(bmp_vector, subbasin_raster)

        self.structure = structure

    @property
    def dugout_df(self)->pd.DataFrame:
        dugouts = [Dugout(att) for att in self.structure.attributes]
        return pd.DataFrame([vars(rb) for rb in dugouts])

