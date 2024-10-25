from whitebox_workflows import Raster
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
from ..database.bmp.bmp_scenarios import BMP_scenarios
from ..names import Names
from .bmp_type import BMPParameters, BMPDistributions
import pandas as pd

class BMP:
    def __init__(self,bmp_vector, subbasin_raster:Raster,):
        self.bmp_vector = bmp_vector
        self.subbasin_raster = subbasin_raster

        self.__ids = None
        self.__subbasins = None
        self.__bmp_raster = None
    
    @property
    def ids(self)->list:
        """unique ids"""
        if self.__ids is None:
            self.__ids = VectorExtension.get_unique_ids(self.bmp_vector)

        return self.__ids
    
    @property
    def bmp_raster(self)->Raster:
        if self.__bmp_raster is None:
            self.__bmp_raster = VectorExtension.vector_to_raster(self.bmp_vector, self.subbasin_raster)

        return self.__bmp_raster

    @property
    def subbasins(self)->dict:
        """Get id and subbasin dictionary"""
        if self.__subbasins is None:
            self.__subbasins = RasterExtension.get_zonal_statistics(self.subbasin_raster, self.bmp_raster,"max","subbasin")["subbasin"].to_dict()

        return self.__subbasins
    
    @staticmethod
    def generate_bmp_scenarios_df(bmp_types:list)->pd.DataFrame:
        bmps = [BMP_scenarios(type, BMPDistributions[type], BMPParameters[type]) for type in bmp_types]
        return pd.DataFrame([vars(rb) for rb in bmps])
        













    

    