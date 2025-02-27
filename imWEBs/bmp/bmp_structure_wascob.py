from .bmp import BMP
from whitebox_workflows import Vector, Raster, VectorGeometryType
import pandas as pd
from ..database.bmp.bmp_41_wascob import Wascob
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
from .bmp_structure_tile_drain import StructureBMPTileDrain
import numpy as np

class StructureBMPWascob(BMP):
    field_name_wascob_start_year = "StartYear"    
    field_name_wascob_start_month = "StartMon"
    field_name_wascob_start_day = "StartDay" 
    field_name_wascob_berm_elevation = "BermElev"
    field_name_wascob_dead_volume = "DeadV"
    field_name_wascob_dead_area = "DeadA"
    field_name_wascob_normal_volume = "NormV"
    field_name_wascob_normal_area = "NormA"
    field_name_wascob_max_volume = "MaxV"
    field_name_wascob_max_area = "MaxA"
    field_name_wascob_drainage_capacity = "MaxQ"
    field_name_wascob_field_id = "FieldID"
    field_name_wascob_tile_drain_id = "TdrainID"

    fields_wascob = [
        field_name_wascob_start_year,
        field_name_wascob_start_month,
        field_name_wascob_start_day,
        field_name_wascob_berm_elevation,
        field_name_wascob_dead_volume,
        field_name_wascob_dead_area,
        field_name_wascob_normal_volume,
        field_name_wascob_normal_area,
        field_name_wascob_max_volume,
        field_name_wascob_max_area,
        field_name_wascob_drainage_capacity,
        field_name_wascob_field_id,
        field_name_wascob_tile_drain_id
    ]

    def __init__(self, 
                 bmp_vector:Vector, 
                 subbasin_raster:Raster, 
                 field_vector:Vector,
                 tile_drain: StructureBMPTileDrain,
                 reach_parameter_df:pd.DataFrame):
        super().__init__(bmp_vector, subbasin_raster)

        self.tile_drain = tile_drain
        self.field_vector = field_vector
        self.reach_receive_reach_dict = reach_parameter_df[["reach_id","receive_reach_id"]].astype({"reach_id":"int","receive_reach_id":"int"}).set_index("reach_id")["receive_reach_id"].to_dict()
       

    @property
    def wascob_df(self)->pd.DataFrame:
        dict_start_year = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_start_year, int)
        dict_start_month = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_start_month, int)
        dict_start_day = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_start_day, int)
        
        dict_start_day = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_start_day, int)

        dict_dead_volume = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_dead_volume, float)
        dict_dead_area = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_dead_area, float)
        dict_normal_volume = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_normal_volume, float)
        dict_normal_area = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_normal_area, float)
        dict_max_volume = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_max_volume, float)
        dict_max_area = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_max_area, float)
        
        dict_capacity = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_drainage_capacity, float)
        dict_elevation = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_berm_elevation, float)
        
        dict_field = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_field_id, int)
        dict_tile_drain = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_tile_drain_id, int)
    
        dict_subbasin_area = RasterExtension.get_category_area_ha_dataframe(self.subbasin_raster, "subbasin_area_ha")["subbasin_area_ha"].to_dict()
        
        field_ids = VectorExtension.get_unique_ids(self.field_vector, True)                                      

        wascobs = []
        for id in self.ids:
            if(dict_field[id] not in field_ids):
                raise ValueError(f"The field id {dict_field[id]} assigned for wascob {id} is not available in field shapefile.")
            
            if(dict_tile_drain[id] not in self.tile_drain.tile_drain_outlet_reach):
                raise ValueError(f"The tile drain id {dict_tile_drain[id]} assigned for wascbo {id} is not available in tile drain shapefile.")
            
            wascobs.append(Wascob(id, 
                                  dict_field[id],
                                  self.subbasins[id],
                                  #self.tile_drain.tile_drain_outlet_reach[dict_tile_drain[id]],
                                  self.reach_receive_reach_dict[self.subbasins[id]],
                                  dict_start_year[id],
                                  dict_start_month[id],
                                  dict_start_day[id],
                                  dict_elevation[id],
                                  dict_dead_volume[id],
                                  dict_dead_area[id],
                                  dict_normal_volume[id],
                                  dict_normal_area[id],
                                  dict_max_volume[id],
                                  dict_max_area[id],
                                  dict_capacity[id],                                  
                                  dict_subbasin_area[self.subbasins[id]] #just subbasin area
                                  ))

        return pd.DataFrame([vars(rb) for rb in wascobs])

    @staticmethod
    def validate(wascob_vector:Vector):
        """
        check wascob point shapefile
        """
        if wascob_vector is None:
            return

        #make sure wascob has all required columns
        VectorExtension.check_fields_in_vector(wascob_vector, StructureBMPWascob.fields_wascob)     
        VectorExtension.validate_vector_shape_type(wascob_vector, VectorGeometryType.Point)  

