from whitebox_workflows import WbEnvironment, Raster, Vector,AttributeField, FieldDataType,FieldData, RasterDataType
from io import StringIO
import pandas as pd
import logging
import math
from .vector_extension import VectorExtension
from .names import Names
import numpy as np
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
    def raster_to_vector(raster:Raster, vector_type:str = "polygon", use_fid = False)->Vector:
        """Convert raster to vector and add an id column as the value"""
        wbe = WbEnvironment()

        #there is no need to consider lines
        vector = None
        if vector_type == "point":
            vector = wbe.raster_to_vector_points(raster)
        elif vector_type == "polygon":
            vector = wbe.raster_to_vector_polygons(raster)
        else:
            vector = wbe.raster_to_vector_lines(raster)

        return VectorExtension.add_id_for_raster_value(vector, use_fid)

    @staticmethod 
    def get_number_of_valid_cell(raster:Raster):
        """Get number of valid cells"""
        rows = raster.configs.rows
        cols = raster.configs.columns
        no_data = raster.configs.nodata
        rowCount = 0
        for row in range(rows):
            for col in range(cols):
                if raster[row, col] != no_data:
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
        if type(lookup_dict) is list:
            dict = {}
            for item in lookup_dict:
                dict[item[0]] = item[1]

        for row in range(raster.configs.rows):
            for col in range(raster.configs.columns):
                if mask_raster is None or mask_raster[row, col] > 0:
                    old_id = int(raster[row, col])
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
            int(standar_raster_config.resolution_x) == int(check_raster_config.resolution_x) and \
            int(standar_raster_config.resolution_y) == int(check_raster_config.resolution_y) and \
            math.fabs(standar_raster_config.east - check_raster_config.east) <= standar_raster_config.resolution_x and \
            math.fabs(standar_raster_config.west - check_raster_config.west) <= standar_raster_config.resolution_y and \
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
        
        return df[stat_type] if isinstance(stat_type, list) else df[stat_type].to_frame()    
    
    @staticmethod
    def get_majority_count(input_data_raster:Raster, feature_definition_raster:Raster)->dict[int, int]:
        """Get the majority count of input data raster in each feature definition raster"""

        rows = input_data_raster.configs.rows
        cols = input_data_raster.configs.columns
        nodata_input = input_data_raster.configs.nodata
        nodata_feature = feature_definition_raster.configs.nodata

        majority_count = {}
        for row in range(rows):
            for col in range(cols):
                if input_data_raster[row, col] != nodata_input and feature_definition_raster[row,col] != nodata_feature:
                    input_id = int(input_data_raster[row, col])
                    feature_id = int(feature_definition_raster[row, col])

                    if feature_id not in majority_count:
                        majority_count[feature_id] = {}
                    if input_id not in majority_count[feature_id]:
                        majority_count[feature_id][input_id] = 0
                    
                    majority_count[feature_id][input_id] = majority_count[feature_id][input_id] + 1
        
        feature_counts = {}
        for feature, counts in majority_count.items():
            feature_counts[feature] = max(counts, key = counts.get)

        return feature_counts
    
    @staticmethod
    def get_overlay_raster(spatial1_ras:Raster, spatial2_ras:Raster):
        spatial1_ras_max = spatial1_ras.configs.maximum   
        if spatial1_ras_max == float('-inf') or spatial1_ras_max == float('inf'):
            spatial1_ras_max = RasterExtension.get_max_value(spatial1_ras)   
        raster1_max = int(math.pow(10, int(math.log10(spatial1_ras_max)) + 2))

        #make a new raster with a unique id combining both raster 1 and raster 2
        rows = spatial1_ras.configs.rows
        cols = spatial1_ras.configs.columns
        no_data1 = spatial1_ras.configs.nodata
        no_data2 = spatial2_ras.configs.nodata
        
        wbe = WbEnvironment()
        configs = spatial1_ras.configs
        configs.data_type = RasterDataType.I64
        overlay_raster = wbe.new_raster(configs)

        temp = np.zeros((rows, cols), dtype = int)
        for row in range(rows):
            for col in range(cols):
                if spatial1_ras[row, col] != no_data1 and spatial2_ras[row, col] != no_data2:
                    id = spatial1_ras[row, col] + spatial2_ras[row, col] * raster1_max
                    temp[row,col]  = int(id)
        
        for row in range(rows):
            for col in range(cols):
                if temp[row,col] > 0:
                    overlay_raster[row, col] = temp[row,col]                 
 
        return overlay_raster, raster1_max
    
    @staticmethod
    def get_overlay_area(spatial1_ras:Raster, spatial2_ras:Raster, name1:str, name2:str, area_column_name = "")->pd.DataFrame:
        """
        Overlay raster 1 and raster 2 and calculate the area of each unique polygon as a pandas dataframe
        """
        merged_raster, raster1_max = RasterExtension.get_overlay_raster(spatial1_ras, spatial2_ras)
        area_col = area_column_name if (area_column_name is not None and len(area_column_name) > 0) else Names.field_name_area
        df = RasterExtension.get_category_area_ha_dataframe(merged_raster,area_col)
        df[name1] = df.index % raster1_max
        df[name2] = (df.index - df[name1]) / raster1_max

        return df
    
    @staticmethod
    def get_dict_with_max_area_in_another_raster(spatial1_ras:Raster, spatial2_ras:Raster)->dict:
        """
        Get the id of raster 2 in raster 1 which has the largest area, return a dictionary with key as raster1 id and value as raster2 id which has the largest area. 
        """

        #get overlay area
        df = RasterExtension.get_overlay_area(spatial1_ras, spatial2_ras, "raster1","raster2")
        
        #get the rows with max area for each ids in raster 1
        max_area_idx = df.groupby("raster1")[Names.field_name_area].idxmax()        
        df_max_area = df.loc[max_area_idx,["raster1","raster2"]].astype({"raster1":"int","raster2":"int"})

        #generate the dictionary and return
        return df_max_area.set_index("raster1")["raster2"].to_dict()

    # @staticmethod
    # def get_overlay_raster_without_multiparts(spatial1_ras:Raster, spatial2_ras:Raster, spatial1_id_column_name:str, spatial2_id_column_name:str)-> tuple[Raster, Vector]:
    #     """
    #     get overlayer raster and separate multiparts polygons. The values of the result raster will have ids starting from 1
        
    #     caution: this doesn't work probably due to the bugs in whitebox workflow
        
    #     """
    #             #this will assign unique values for each unique combination of spatial1 and spatial2
    #     raster, raster1_max = RasterExtension.get_overlay_raster(spatial1_ras, spatial2_ras)
    #     wbe = WbEnvironment()
    #     wbe.write_raster(raster, r"C:\Work\imWEBs\test\gg\watershed\output\test1.tif")
    #     raster = wbe.read_raster(r"C:\Work\imWEBs\test\gg\watershed\output\test1.tif")

    #     #convert to vector to separate multiparts
    #     vector = RasterExtension.raster_to_vector(raster, "polygon", True)
    #     wbe.write_vector(vector, r"C:\Work\imWEBs\test\gg\watershed\output\test1.shp")
    #     vector = wbe.read_vector(r"C:\Work\imWEBs\test\gg\watershed\output\test.shp")

    #     #convert to raster and use FID as the raster value
    #     #in this raster, the multiparts will have differnt ids
    #     raster = wbe.vector_polygons_to_raster(input = vector, field_name = Names.field_name_id, base_raster = spatial2_ras)
        
    #     wbe.write_raster(raster, r"C:\Work\imWEBs\test\gg\watershed\output\test2.tif")

    #     #add and populate two foreign id columns and id column
    #     vector.add_attribute_field(AttributeField(Names.field_name_id, FieldDataType.Int, 10, 0))
    #     vector.add_attribute_field(AttributeField(spatial1_id_column_name, FieldDataType.Int, 10, 0))
    #     vector.add_attribute_field(AttributeField(spatial2_id_column_name, FieldDataType.Int, 10, 0))

    #     dict_spatial1 = RasterExtension.get_zonal_statistics(spatial1_ras, raster,"max","col1")["col1"].to_dict() 
    #     dict_spatial2 = RasterExtension.get_zonal_statistics(spatial2_ras, raster,"max","col2")["col2"].to_dict() 

    #     for i in range(vector.num_records):
    #         vector.set_attribute_value(i,Names.field_name_id,FieldData.new_int(i + 1))
    #         vector.set_attribute_value(i,spatial1_id_column_name,FieldData.new_int(int(dict_spatial1[i+1])))
    #         vector.set_attribute_value(i,spatial2_id_column_name,FieldData.new_int(int(dict_spatial2[i+1])))

    #     return (raster, vector)        