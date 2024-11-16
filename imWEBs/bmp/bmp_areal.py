from .bmp import BMP
from whitebox_workflows import Vector, Raster
from ..raster_extension import RasterExtension
from typing import Dict, List, Tuple
import math
import numpy as np

class ArealBMP(BMP):
    def __init__(self,
                 bmp_vector:Vector,
                 flow_direction_raster:Raster,
                 subbasin_raster:Raster,
                 reach_raster:Raster,
                 dem_raster:Raster):
        super().__init__(bmp_vector, subbasin_raster)

        self.flow_direction_raster = flow_direction_raster
        self.reach_raster = reach_raster
        self.dem_raster = dem_raster
        
        self.__contribution_area_ha = None
        self.__contribution_area_subbasin_ratio = None
        self.__bmp_locations = None
        self.__reach_ids = None
        self.__reach_distance = None
        self.__reach_elevation_drop = None    
   
    @property
    def contribution_area_ha(self)->dict:
        if self.__contribution_area_ha is None:
            self.__contribution_area_ha = RasterExtension.get_zonal_statistics(self.flow_direction_raster, self.bmp_raster,"max","contribution_area_ha") * self.subbasin_raster.configs.resolution_x * self.subbasin_raster.configs.resolution_y / 10000.0 
            self.__contribution_area_ha = self.__contribution_area_ha["contribution_area_ha"].to_dict()

        return self.__contribution_area_ha
    
    @property
    def contribution_area_subbasin_ratio(self)->dict:
        if self.__contribution_area_subbasin_ratio is None:
            self.__contribution_area_subbasin_ratio = {}

            subbasin_area_ha = RasterExtension.get_category_area_ha_dataframe(self.subbasin_raster, "subbasin_area_ha")["subbasin_area_ha"].to_dict()
            for id, subbasin in self.subbasins:
                self.__contribution_area_subbasin_ratio[id] = self.contribution_area_ha[id] / subbasin_area_ha[subbasin]

        return self.__contribution_area_subbasin_ratio

    @property
    def bmp_locations(self) -> Dict[int, List[Tuple[int, int]]]:
        """The row and col index of each bmp"""
        if self.__bmp_locations is None:
            self.__bmp_locations = {}        
            rows = self.bmp_raster.configs.rows
            cols = self.bmp_raster.configs.columns
            for row in range(rows):
                for col in range(cols):
                    value = self.bmp_raster[row, col]
                    if value > 0:
                        id = int(value)
                        if id not in self.__bmp_raster:
                            self.__bmp_raster[id] = []
                        self.__bmp_raster[id].append((row, col))
            
        return self.__bmp_locations
        
    @property
    def reach_ids(self)->dict:
        """The downstream reach id for each bmp"""
        if self.__reach_ids is None:
            self.__reach_ids = {}
            for id, cells in self.bmp_locations.items():
                for cell in cells:
                    reach = self.__get_down_stream_row_col(cell[0], cell[1], -1)
                    if reach is not None:
                        self.__reach_ids[id] = self.reach_raster[reach[0], reach[1]]
                        break

                if id not in self.__reach_ids:
                    self.__reach_ids[id] = -1

        return self.__reach_ids
    
    @property
    def reach_distance(self)->dict:
        """the distance to reach"""
        if self.__reach_distance is None: 
            self.__reach_distance = {}
            for id, cells in self.bmp_locations.items():
                out = -1
                for cell in cells:
                    distance = self.__get_downstream_distance(cell[0], cell[1], self.reach_ids[id])
                    if distance > 0 and (distance < out or out < 0):
                        out = distance

                self.__reach_distance[id] = max(out, 0)

        return self.__reach_distance
    
    @property 
    def reach_elevation_drop(self)->dict:
        """The elevation drop from the bmp to the reach"""
        if self.__reach_elevation_drop is None:
            self.__reach_elevation_drop = {}
            for id, cells in self.bmp_locations.items():
                out = -1
                for cell in cells:
                    reach = self.__get_down_stream_row_col(cell[0], cell[1], self.reach_ids[id])
                    if reach is not None:
                        elevation_drop = self.dem_raster[cell[0], cell[1]] - self.dem_raster[reach[0], reach[1]]
                        if elevation_drop > 0 and (elevation_drop < out or out < 0):
                            out = elevation_drop

                self.__reach_elevation_drop[id] = max(out, 0)     

        return self.__reach_elevation_drop      
    
    def __get_down_stream_row_col(self, row, col, reach_id):
        """get first row and col of downstream reach"""
        dx = [1, 1, 1, 0, -1, -1, -1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        ln_of_2 = np.log(2)
        x, y = col, row

        while True:
            flow_dir = self.flow_direction_raster[y, x]
            if flow_dir > 0:
                c = int(np.log(flow_dir) / ln_of_2)
                if c > 7:
                    return [0, 0]
                if self.reach_raster[y, x] > 0 and reach_id == int(self.reach_raster[y, x]):
                    return [y, x]
                elif reach_id < 0 and self.reach_raster[y, x] > 0:
                    return [y, x]

                x += dx[c]
                y += dy[c]
            else:
                return None

        return None

    def __get_downstream_distance(self, row, col, reach_id):
        diag_dist = math.sqrt(self.reach_raster.configs.resolution_x ** 2 + self.reach_raster.configs.resolution_y ** 2)

        dx = [1, 1, 1, 0, -1, -1, -1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        dir_dist = [diag_dist, self.reach_raster.configs.resolution_x, diag_dist, self.reach_raster.configs.resolution_y,
                    diag_dist, self.reach_raster.configs.resolution_x, self.reach_raster.configs.resolution_y, diag_dist]
        ln_of_2 = math.log(2)

        x, y = col, row
        total_dist = 0

        while True:
            flow_dir = self.flow_direction_raster[y, x]
            if flow_dir > 0:
                c = int(math.log(flow_dir) / ln_of_2)
                if c > 7:
                    return -1
                if self.reach_raster[y, x] > 0 and reach_id == int(self.reach_raster[y, x]):
                    break
                elif reach_id < 0 and self.reach_raster[y, x] > 0:
                    break

                x += dx[c]
                y += dy[c]
                total_dist += dir_dist[c]
            else:
                return -1

        return total_dist