from whitebox_workflows import WbEnvironment, Raster, Vector
from io import StringIO
import pandas as pd
import logging
import math
from .vector_extension import VectorExtension
from .names import Names
logger = logging.getLogger(__name__)



class RasterExtension:
    @staticmethod
    def get_max_value(raster:Raster)->float:
        """get max value in a raster"""
        rows = raster.configs.rows
        cols = raster.configs.columns
        noddata = raster.configs.nodata
        max_value = float("-inf")
        for row in range(rows):
            for col in range(cols):
                if raster[row, col] != noddata:
                    if max_value < raster[row, col]:
                        max_value = raster[row, col]
        return max_value         

    @staticmethod
    def raster_to_vector(raster:Raster, vector_type:str = "polygon")->Vector:
        """Convert raster to vector and add an id column as the value"""
        wbe = WbEnvironment()

        #there is no need to consider lines
        vector = None
        if vector_type == "point":
            vector = wbe.raster_to_vector_points(raster)
        else:
            vector = wbe.raster_to_vector_polygons(raster)

        return VectorExtension.add_id_for_raster_value(vector)

    @staticmethod 
    def get_number_of_valid_cell(raster:Raster):
        """Get number of valid cells"""
        rows = raster.configs.rows
        cols = raster.configs.columns
        rowCount = 0
        for row in range(rows):
            for col in range(cols):
                if raster[row, col] > 0:
                    rowCount += 1 #number of valid cell
        return rowCount    

    @staticmethod
    def flow_dir_to_index_delta(flow_dir):
        if  int(flow_dir) not in RasterExtension.flow_dir_to_index_delta:
            raise ValueError(f"{flow_dir} is not an invalid flow direction value.")
        
        delta = RasterExtension.flow_dir_to_index_delta[int(flow_dir)]
        dx = delta[0]
        dy = delta[1]
        return dx, dy

    @staticmethod
    def reclassify(raster:Raster, lookup_dict, mask_raster:Raster = None)->Raster:
        """
        reclassify raster with dictionary. 

        it could be also done with wbe.reclass but have some issues
        """

        wbe = WbEnvironment()
        mapped_raster = wbe.new_raster(raster.configs)
        no_data = raster.configs.nodata

        dict = lookup_dict
        if lookup_dict is list:
            dict = {}
            for item in lookup_dict:
                dict[item[0]] = item[1]

        for row in range(raster.configs.rows):
            for col in range(raster.configs.columns):
                if mask_raster is None or mask_raster[row, col] > 0:
                    old_id = raster[row, col]
                    if old_id != no_data:
                        mapped_raster[row,col] = dict[old_id]

        return mapped_raster

    @staticmethod
    def filter_by_values(raster:Raster, values:list)->Raster:
        """
        remove values that are not included in the given value list
        """
        wbe = WbEnvironment()
        filtered_raster = wbe.new_raster(raster.configs)
        no_data = raster.configs.nodata
        for row in range(raster.configs.rows):
            for col in range(raster.configs.columns):
                if raster[row, col] != no_data and raster[row, col] in values:
                    filtered_raster[row, col] = raster[row, col]

        return filtered_raster

    @staticmethod
    def compare_raster_extent(raster1:Raster, raster2:Raster):
        """Check if the raster have same size as the standard raster """
        standar_raster_config = raster1.configs
        check_raster_config = raster2.configs

        return standar_raster_config.rows == check_raster_config.rows and \
            standar_raster_config.columns == check_raster_config.columns and \
            standar_raster_config.resolution_x == check_raster_config.resolution_x and \
            standar_raster_config.resolution_y == check_raster_config.resolution_y and \
            math.fabs(standar_raster_config.east - check_raster_config.east) <= standar_raster_config.resolution_x and \
            math.fabs(standar_raster_config.west == check_raster_config.west) <= standar_raster_config.resolution_y and \
            standar_raster_config.epsg_code == check_raster_config.epsg_code
    
    @staticmethod
    def check_rasters(rasters:dict)->bool:
        """Compare all the rasters in the dictionary and return trun only when all of them has the same resolution and dimension."""
        if len(rasters) <= 1:
            return True
        
        is_same = True
        standard_raster = None
        for key, value in rasters.items():
            if standard_raster is None:
                standard_raster = value
                continue
            
            if not RasterExtension.compare_raster_extent(standard_raster, value):
                raise ValueError(f"The extend of {value.file_name} doesn't match {standard_raster.file_name}")

        return is_same

    @staticmethod
    def get_category_area_ha_dataframe(raster:Raster, area_col_name:str)->pd.DataFrame:
        """Get area of each raster value in ha"""
        wbe = WbEnvironment()
        class_area = wbe.raster_area(raster)
        df = pd.read_csv(StringIO(class_area[1]),skiprows=1, index_col=0, names=[Names.field_name_id,area_col_name])
        df = df / 10000 #convert to ha
        return df
  
    @staticmethod
    def get_zonal_statistics(input_data_raster:Raster, feature_definition_raster:Raster, stat_type, name:str = None)->pd.DataFrame:
        """do zonal statistics and return requested state value as dictionary"""

        wbe = WbEnvironment()

        #do zonal statistics
        stats = wbe.zonal_statistics(input_data_raster,feature_definition_raster)

        #read the result string to dataframe
        df = pd.read_csv(StringIO(stats[1]), sep ="|",  skiprows=5, index_col=1, names=["first","ID","mean","median","min","max","range","stdev","total","last"])
        
        #need to conver the index to the real id
        #this is not necessary for next release
        #it seems this has been fixed
        #df.index = df.index + 1

        if name is not None:
            df[name] = df[stat_type]
            return df[name].to_frame()
        
        return df[stat_type]    
    