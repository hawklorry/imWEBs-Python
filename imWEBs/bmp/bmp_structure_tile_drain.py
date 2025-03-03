from .bmp import BMP
from whitebox_workflows import Vector, Raster, VectorGeometryType
import pandas as pd
from ..delineation.structure import Structure
from ..database.bmp.bmp_19_tile_drain_management import TileDrainParameter
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
import numpy as np

class StructureBMPTileDrain(BMP):
    field_name_tile_drain_depth = "Depth"
    field_name_tile_drain_spacing = "Spacing"
    field_name_tile_drain_radius = "Radius"
    field_name_tile_drain_elevation = "Elevation"
    field_name_tile_drain_start_year = "StartYear"
    field_name_tile_drain_start_month = "StartMon"
    field_name_tile_drain_start_day = "StartDay"

    fields_tile_drain = [
        field_name_tile_drain_depth,
        field_name_tile_drain_spacing,
        field_name_tile_drain_radius,
        field_name_tile_drain_elevation,
        field_name_tile_drain_start_year,
        field_name_tile_drain_start_month,
        field_name_tile_drain_start_day
    ]

    def __init__(self, tile_drain_vector:Vector, 
                 tile_drain_outlet_pour_points_raster:Raster, 
                 tile_drain_raster:Raster, 
                 subbasin_raster:Raster, 
                 reach_parameter_df:pd.DataFrame, 
                 field_raster:Raster, 
                 dem_raster:Raster):
        super().__init__(tile_drain_vector, subbasin_raster)

        self.field_raster = field_raster
        self.dem_raster = dem_raster
        self.bmp_raster_original = tile_drain_raster
        self.reach_contribution_area_dict = reach_parameter_df[["reach_id","contribution_area"]].astype({"reach_id":"int","contribution_area":"float"}).set_index("reach_id")["contribution_area"].to_dict()
        self.reach_receive_reach_dict = reach_parameter_df[["reach_id","receive_reach_id"]].astype({"reach_id":"int","receive_reach_id":"int"}).set_index("reach_id")["receive_reach_id"].to_dict()
        
        self.tile_drain_outlet_raster = tile_drain_outlet_pour_points_raster
        self.__dict_tile_drain_reach = None
        self.__dict_tile_drain_subbasin = None

    @property
    def dict_tile_drain_subbasin(self)->dict:
        """Get subbasin for each tile drain with the lowest average elevation. Only the portion inside the tile drain will be accounted."""
        if self.__dict_tile_drain_subbasin is None:
            #overlay tile drain and subbasin to get the area of the each unique combination.
            tiledrain_subbasin_raster, tile_drain_max_id = RasterExtension.get_overlay_raster(self.bmp_raster, self.subbasin_raster)
            df_tile_drain_subbasin_overlay_mean_elevation = RasterExtension.get_zonal_statistics(self.dem_raster, tiledrain_subbasin_raster,"mean")        
            df_tile_drain_subbasin_overlay_mean_elevation["tile_drain"] = df_tile_drain_subbasin_overlay_mean_elevation.index % tile_drain_max_id
            df_tile_drain_subbasin_overlay_mean_elevation["subbasin"] = (df_tile_drain_subbasin_overlay_mean_elevation.index - df_tile_drain_subbasin_overlay_mean_elevation["tile_drain"]) / tile_drain_max_id
            
            #get the rows with max area for each ids in raster 1
            min_elevation_idx = df_tile_drain_subbasin_overlay_mean_elevation.groupby("tile_drain")["mean"].idxmin()        
            df_tile_drain_subbasin_overlay_mean_elevation = df_tile_drain_subbasin_overlay_mean_elevation.loc[min_elevation_idx,["tile_drain","subbasin"]].astype({"tile_drain":"int","subbasin":"int"})
            self.__dict_tile_drain_subbasin = df_tile_drain_subbasin_overlay_mean_elevation.set_index("tile_drain")["subbasin"].to_dict()

        return self.__dict_tile_drain_subbasin

    @property
    def tile_drain_outlet_reach(self)->dict:
        """
        Looking for outlet reach for each tile drain field, key = tile drain id, value = reach id

        1. If tile drain outlet shapefile is provied, the reach id will be the subbasin id where the outlet is located. 
        2. If tile drain outlet shapefile is not provided or the outlet field is empty, the reach id will be searched with following steps. 
            1) find the lowest subbasin the tile drain covers,
            2) if the reach contribution area < 10 ha, trace downsteam to find the first reach where the contribution area > 10 ha
        
        """
        if self.__dict_tile_drain_reach is not None:
            return self.__dict_tile_drain_reach
        
        tile_drain_ids = list(self.dict_tile_drain_subbasin.keys())
        tile_drain_ids.sort()
        self.__dict_tile_drain_reach = {} 
    
        #use tile drain outlet vector first
        if self.tile_drain_outlet_raster is not None:
            #find the subbasin for each tile drain outlet
            dict_tile_drain_outlet_subbasin = RasterExtension.get_zonal_statistics(self.subbasin_raster, self.tile_drain_outlet_raster,"mean","subbasin")["subbasin"].to_dict()

            #loop through all tile drains
            for tile_drain_id in tile_drain_ids:
                #loop through current reach and all downstream reaches to find the tile drain outlet
                #we will use the reach when there is an outlet on it.
                reach = self.dict_tile_drain_subbasin[tile_drain_id]
                while reach not in dict_tile_drain_outlet_subbasin.values():
                    reach = self.reach_receive_reach_dict[reach]
                    if reach == 0:
                        break

                if reach > 0:
                    self.__dict_tile_drain_reach[tile_drain_id] = reach
               
            #if all tile drain field already have outlets, return
            if len(tile_drain_ids) == len(list(self.__dict_tile_drain_reach.keys())):
                return self.__dict_tile_drain_reach  

        #add tile drains that doesn't have outlet yet or the outlets are not found in the outlet shapefile
        for tile_drain_id in tile_drain_ids:
            #skip tile drains that already have an reach outlet
            if tile_drain_id in self.__dict_tile_drain_reach:
                continue
            
            #the first reach
            reach = self.dict_tile_drain_subbasin[tile_drain_id]

            #check reach drainage area, if < 10ha, search downstream until find one that > 10ha
            while self.reach_contribution_area_dict[reach] < 10:
                reach = self.reach_receive_reach_dict[reach]
                if reach == 0:
                    break

            #use it
            self.__dict_tile_drain_reach[tile_drain_id] = reach

        #if all tile drain field already have outlets, return
        tile_drains_having_reach = list(self.__dict_tile_drain_reach.keys())
        tile_drains_having_reach.sort()
        if not np.array_equal(tile_drain_ids, tile_drains_having_reach):
            missing_tile_drains = [tile_drain for tile_drain in tile_drain_ids if tile_drain not in tile_drains_having_reach]
            raise ValueError(f"Reaches were not found for following tile drains: {missing_tile_drains}.")

        #return
        return self.__dict_tile_drain_reach
            
    @property
    def tile_drain_outlet_drainage_df(self)->pd.DataFrame:
        #get unique reaches
        reaches = set(self.tile_drain_outlet_reach.values())

        #create the df
        df = pd.DataFrame(list(reaches), columns=["Reach"])
        df["Id"] = df.index + 1
        df["DrainageCapacity"] = 3800

        return df

    @property
    def tile_drain_df(self)->pd.DataFrame:
        dict_depth = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_depth, float)
        dict_spacing = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_spacing, float)
        dict_radius = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_radius, float)
        dict_start_year = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_start_year, int)
        dict_start_month = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_start_month, int)
        dict_start_day = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_start_day, int)
        dict_field = RasterExtension.get_majority_count(self.field_raster, self.bmp_raster)
        dict_elevation = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_elevation, float)      

        tile_drains = []
        #some tile drain field may not be included.
        for id, depth in dict_depth.items():
            if id not in self.tile_drain_outlet_reach:
                continue
            tile_drains.append(TileDrainParameter(
                id,
                dict_field[id],
                self.tile_drain_outlet_reach[id],
                dict_elevation[id],
                depth,
                dict_spacing[id],
                dict_radius[id],
                dict_start_year[id],
                dict_start_month[id],
                dict_start_day[id]
            ))

        return pd.DataFrame([vars(rb) for rb in tile_drains])

    @staticmethod
    def validate(tile_drain_boundary_vector:Vector,tile_drain_outlet_vector:Vector):
        """
        check tile drain boundary layer
        """
        if tile_drain_boundary_vector is not None:       
            #make sure tile drain has all required columns
            VectorExtension.check_fields_in_vector(tile_drain_boundary_vector, StructureBMPTileDrain.fields_tile_drain)
            VectorExtension.validate_vector_shape_type(tile_drain_boundary_vector, VectorGeometryType.Polygon)
        
        if tile_drain_outlet_vector is not None:
            VectorExtension.validate_vector_shape_type(tile_drain_outlet_vector, VectorGeometryType.Point)
