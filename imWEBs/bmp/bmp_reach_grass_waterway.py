from .bmp_reach import ReachBMP
from ..database.bmp.bmp_06_grass_waterway import GrassWaterWay
from ..database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from whitebox_workflows import Vector, Raster, VectorGeometryType
from ..vector_extension import VectorExtension
import logging
import math
import pandas as pd
logger = logging.getLogger(__name__)

class ReachBMPGrassWaterWay(ReachBMP):
    def __init__(self, grass_waterway_vector:Vector, 
                subbasin_raster:Raster, 
                flow_dir_raster:Raster, 
                reach_parameter_df:pd.DataFrame):
        super().__init__(grass_waterway_vector, subbasin_raster)       
        self.__grass_waterways = None
        self.flow_dir_raster = flow_dir_raster
        self.reach_length_dict = reach_parameter_df[["reach_id","length"]].astype({"reach_id":"int","length":"float"}).set_index("reach_id")["length"].to_dict()
        self.__dict_subbasin_grass_waterway_length = None
        self.__id_subbasins = {}

    @staticmethod
    def validate(grass_waterway_vector:Vector):
        if grass_waterway_vector is None:
            return
        
        if grass_waterway_vector.header.shape_type != VectorGeometryType.PolyLine and grass_waterway_vector.header.shape_type != VectorGeometryType.PolyLineM and grass_waterway_vector.header.shape_type != VectorGeometryType.PolyLineZ:
            raise ValueError("The provided grass waterway shapefile is not polygline shape.")

    @property
    def dict_subbasin_grass_waterway_length(self):
        if self.__dict_subbasin_grass_waterway_length is None:
            self.__dict_subbasin_grass_waterway_length = {}
            flow_dir_horizontal = [2, 32]
            flow_dir_vertical = [8, 128]

            width = self.bmp_raster.configs.resolution_x
            heigth = self.bmp_raster.configs.resolution_y
            diagonal = math.sqrt(width * width + heigth*heigth)

            no_data = self.bmp_raster.configs.nodata
            for row in range(self.bmp_raster.configs.rows):
                for col in range(self.bmp_raster.configs.columns):
                    if self.bmp_raster[row, col] == no_data or self.subbasin_raster[row,col] <= 0:
                        continue
                    
                    subbasin = self.subbasin_raster[row,col]
                    flow_dir = self.flow_dir_raster[row,col]

                    length = width if flow_dir in flow_dir_horizontal else (heigth if flow_dir in flow_dir_vertical else diagonal)
                    
                    if subbasin in self.__dict_subbasin_grass_waterway_length:
                        self.__dict_subbasin_grass_waterway_length[subbasin] += length
                    else:
                        self.__dict_subbasin_grass_waterway_length[subbasin] = length

        return self.__dict_subbasin_grass_waterway_length
    
    @property
    def id_subbasins(self)->dict:
        return self.__id_subbasins

    @property
    def grass_waterways(self)->list[GrassWaterWay]:
        if self.__grass_waterways is None:
            self.__grass_waterways = []

            index = 1      
            self.__id_subbasins = {}
            for subbasin, length in self.dict_subbasin_grass_waterway_length.items():
                self.__grass_waterways.append(GrassWaterWay(index, subbasin, round(length) if length < self.reach_length_dict[subbasin] else self.reach_length_dict[subbasin]))
                self.__id_subbasins[index] = subbasin
                index += 1

        return self.__grass_waterways