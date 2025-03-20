import os
from whitebox_workflows import Raster, Vector
from .parameters import Parameters
from .database.bmp.reach import Reach
import numpy as np
import math
from .folder_base import FolderBase
from .names import Names
from .inputs import Inputs
from .delineation.structure import Structure
from .raster_extension import RasterExtension
from .delineation.delineation import Delineation
from .vector_extension import VectorExtension
from .database.parameter.parameter_database import ParameterDatabase
import pandas as pd
from .bmp.bmp_type import DefaultScenarioId
from .iuh import IUH
from .database.bmp.subarea import SubArea
from .bmp.bmp_structure_tile_drain import StructureBMPTileDrain
from .database.hydroclimate.hydroclimate_database import HydroClimateDatabase

import logging
logger = logging.getLogger(__name__)
        
class Outputs(FolderBase):
    """
    Output folder where all intermediate and final processed files are saved
    """
    def __init__(self, 
                 output_folder:str, 
                 input_folder:str,
                 database_folder:str, 
                 stream_threshold_area_ha:float = 10,   #stream thrshold area
                 wetland_min_area_ha:float = 0.1,       #min wetland area
                 design_storm_return_period = 2         #design storm return period for reach width and depth
                 ) -> None:
        super().__init__(output_folder)
        
        self.database_folder = database_folder 
        self.__hydroclimate_database = HydroClimateDatabase(os.path.join(self.database_folder,Names.hydroclimateDatabasename))
        self.inputs = Inputs(input_folder, self.__hydroclimate_database)       

        self.stream_threshold_area_ha = stream_threshold_area_ha
        self.main_stream_threshold_area_ha = 200            #threshold for main stream in ha
        self.design_storm_return_period = design_storm_return_period

        self.wetland_min_area_ha = wetland_min_area_ha
        self.__structures = None
        self.__structure_combined = None
        self.__parameters = None

    @property
    def number_of_valid_cell(self)->int:
        return RasterExtension.get_number_of_valid_cell(self.mask_refined_with_subbasin_raster)
    
    @property
    def number_of_subbasin(self)->int:
        return int(RasterExtension.get_max_value(self.subbasin_raster))
    
    @property
    def hydroclimate_database(self)->HydroClimateDatabase:
        if self.__hydroclimate_database is None:
            self.__hydroclimate_database = HydroClimateDatabase(os.path.join(self.database_folder,Names.hydroclimateDatabasename))

        return self.__hydroclimate_database

    @property
    def parameter(self)->Parameters:
        if self.__parameters is None:
            self.__parameters = Parameters(self.database_folder)

        return self.__parameters
    
#region structures

    @property
    def wetland_raster(self)->Raster:
        """
        create wetland raster
        1. if user provides wetland vector, use it
        2. if not, create an empty raster as it must have one
        """
        raster = self.get_raster(Names.wetlandRasName)

        if raster is None:
            if "wetland" in self.structures:
                raster = self.structures["wetland"].boundary_raster
            else:
                raster = self.inputs.create_new_raster()
            
            raster = self.save_raster(raster, Names.wetlandRasName, True, True)

        return raster
    
    @property
    def feedlot_raster(self)->Raster:
        if "feedlot" in self.structures:
            return self.structures["feedlot"].boundary_processed_raster
        return None
    
    @property
    def feedlot_drainage_area_raster(self)->Raster:
        if "feedlot" in self.structures:
            return self.structures["feedlot"].get_dainage_area_raster(self.flow_direction_raster, self.subbasin_raster)
        return None
    
    @property
    def wascob_drainage_area_raster(self)->Raster:
        raster = self.get_raster(Names.wascobDrainageAreaRasName)

        if raster is None and self.inputs.wascob_vector is not None:
            #find the subbasin for each wascob and create the raster
            wascob_raster = VectorExtension.vector_to_raster(self.inputs.wascob_vector, self.dem_clipped_raster_for_model)
            dict_wascob_subbasin = RasterExtension.get_zonal_statistics(self.subbasin_raster, wascob_raster,"max","subbasin")["subbasin"].to_dict()
            dict_subbasin_wascob = {value: key for key, value in dict_wascob_subbasin.items()}

            rows = self.subbasin_raster.configs.rows
            cols = self.subbasin_raster.configs.columns
            no_data = self.subbasin_raster.configs.nodata
            raster = self.inputs.create_new_raster()
            for row in range(rows):
                for col in range(cols):
                    if self.subbasin_raster[row, col] in dict_subbasin_wascob:
                        raster[row, col] = dict_subbasin_wascob[self.subbasin_raster[row, col]]

            self.save_raster(raster, Names.wascobDrainageAreaRasName)

        return raster 

    @property
    def tile_drain_raster(self)->Raster:
        raster = self.get_raster(Names.tileDrainRasName)

        if raster is None and self.inputs.tile_drain_boundary_vector is not None:
            raster = VectorExtension.vector_to_raster(self.inputs.tile_drain_boundary_vector, self.dem_clipped_raster_for_model)
            self.save_raster(raster, Names.tileDrainRasName)

        return raster
    
    @property
    def tile_drain_outlet_pour_points_vector(self)->Vector:
        vector = self.get_vector(Names.tileDrainOutletPourPointShpName)

        if vector is None and self.inputs.tile_drain_outlet_vector is not None:        
            vector = self.wbe.jenson_snap_pour_points(
                        pour_pts = self.inputs.tile_drain_outlet_vector,
                        streams = self.stream_network_raster,
                        snap_dist = 2000)

            self.save_vector(vector, Names.tileDrainOutletPourPointShpName)

        return vector
    
    @property
    def tile_drain_outlet_pour_points_raster(self)->Vector:
        raster = self.get_raster(Names.tileDrainOutletPourPointRasName)

        if raster is None and self.tile_drain_outlet_pour_points_vector is not None:        
            raster = self.wbe.vector_points_to_raster(self.tile_drain_outlet_pour_points_vector, base_raster = self.dem_clipped_raster_for_model)

            self.save_raster(raster, Names.tileDrainOutletPourPointRasName)

        return raster

    @property
    def structures(self)->dict[str, Structure]:
        if self.__structures is None:
            self.__structures = {}
            logger.info("Initilizing structures ...")
            for type in Structure.structure_types_affection_flow_direction:
                boundary_vector = getattr(self.inputs, f"{type}_boundary_vector")
                if boundary_vector is not None:
                    logger.info(type)
                    self.__structures[type] = Structure(
                        structure_type=type,
                        output_folder=self.folder,
                        dem_raster=self.dem_clipped_burned_filled_raster,
                        structure_polygon_vector = boundary_vector, 
                        structure_outlet_point_vector = getattr(self.inputs, f"{type}_outlet_vector"), 
                        structure_area_threshold_ha = self.wetland_min_area_ha if type == "wetland" else 0)     
                    
        return self.__structures
    
    @property
    def structure_combined_boundary_vector(self)->Vector:
        vector = self.get_vector(Names.structureCombinedBoundaryShpName)

        if vector is None and len(self.structures) > 0:
            vector = VectorExtension.merge_vectors([structure.boundary_original_vector for structure in self.structures.values()])
            self.save_vector(vector, Names.structureCombinedBoundaryShpName)

        return vector
    
    @property
    def structure_combined_outlet_vector(self)->Vector:
        vector = self.get_vector(Names.structureCombinedOutputShpName)

        if vector is None and len(self.structures) > 0:
            vector = VectorExtension.merge_vectors([structure.outlet_vector for structure in self.structures.values()])
            self.save_vector(vector, Names.structureCombinedOutputShpName)

        return vector
    
    @property
    def structure_combined_outlet_raster(self):
        raster = self.get_raster(Names.structureCombinedOutputRasName)

        if raster is None and len(self.structures) > 0:
            raster = self.wbe.vector_points_to_raster(input = self.structure_combined_outlet_vector, 
                                                            field_name = Names.field_name_id,
                                                            base_raster = self.inputs.dem_raster)
            raster = self.save_raster(raster, Names.structureCombinedOutputRasName, True, True)

        return raster

    @property
    def structure_combined(self)->Structure:
        """
        Combined structure used to get the revised flow direction
        """
        if len(self.structures) <= 0:
            return None
        
        if self.__structure_combined is None:
            logger.info("Merging all flow-direction-affecting structures ...")

            self.__structure_combined = Structure(
                structure_type="structureCombined",
                output_folder=self.folder,
                dem_raster=self.dem_clipped_burned_filled_raster,
                structure_polygon_vector = self.structure_combined_boundary_vector,
                structure_outlet_point_vector = self.structure_combined_outlet_vector
            )

        return self.__structure_combined

#endregion
                
#region DEM processing

    @property
    def mask_raster(self):
        raster = self.get_raster(Names.maskRasName)
 
        if raster is None:
            #try user provided boundary shapefile
            if self.inputs.boundary_vector is not None:
                logger.info(f"Creating mask using user-defined boundary shapefile ... ")
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.boundary_vector, 
                                                            base_raster = self.inputs.dem_raster)
                raster = raster.con(f"value == {raster.configs.nodata}", self.inputs.nodata, 1)                
            #try use soil and landuse 
            elif self.inputs.soil_raster is not None and self.inputs.landuse_raster is not None:
                logger.info(f"Creating mask using soil and landuse ... ")
                raster = self.inputs.create_new_raster()
                raster = self.inputs.dem_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, 1)
                raster = self.inputs.soil_raster.con(f"value == {self.inputs.soil_raster.configs.nodata}", self.inputs.nodata, raster)
                raster = self.inputs.landuse_raster.con(f"value == {self.inputs.landuse_raster.configs.nodata}", self.inputs.nodata, raster)

            if raster is not None:
                raster = self.save_raster(raster, Names.maskRasName, True, True)

        return raster
    
    @property
    def mask_refined_with_subbasin_raster(self):
        raster = self.get_raster(Names.maskRefindedWithSubbasinRasName)

        if raster is None:
            logger.info("Refining mask with subbain ...")
            raster = self.subbasin_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, 1)
            raster = self.inputs.soil_raster.con(f"value == {self.inputs.soil_raster.configs.nodata}", self.inputs.nodata, raster)
            raster = self.inputs.landuse_raster.con(f"value == {self.inputs.landuse_raster.configs.nodata}", self.inputs.nodata, raster)

            raster = self.save_raster(raster, Names.maskRefindedWithSubbasinRasName, True, True)

        return raster

    @property 
    def dem_clipped_raster_for_model(self):
        """
        This is the dem clipped by the final subbain raster. This will be the base for parameter.h5
        """
        raster = self.get_raster(Names.demName)

        if raster is None:
            raster = self.mask_refined_with_subbasin_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, self.inputs.dem_raster)
            raster = self.save_raster(raster, Names.demName, True, True)

        return raster

    @property 
    def dem_clipped_raster(self):
        """
        Clipped DEM by mask
        """
        raster = self.get_raster(Names.demClippedName)

        if raster is None:
            logger.info("Masking DEM ...")
            raster = self.mask_raster.con("value == 1", self.inputs.dem_raster, self.inputs.nodata)
            raster = self.save_raster(raster, Names.demClippedName, True, True)

        return raster

    @property 
    def dem_clipped_burned_raster(self):
        """
        Burned DEM with user-provided stream shapefile
        """
        if self.stream_network_user_raster is None:
            return self.dem_clipped_raster

        raster = self.get_raster(Names.demBurnedName)
        if raster is None:
            logger.info("Burning stream ...")
            raster = self.stream_network_user_raster.con(f"value == nodata",
                                                         self.dem_clipped_raster,
                                                         self.dem_clipped_raster - 10)
            raster = self.save_raster(raster, Names.demBurnedName, True, True)

        return raster
    
    @property
    def dem_clipped_burned_filled_raster(self):
        """
        Filled DEM
        """
        raster = self.get_raster(Names.demFilledName)

        if raster is None:
            logger.info("Filling depression ...")
            #raster = self.wbe.breach_depressions_least_cost(self.dem_clipped_burned_raster, flat_increment=0.001, max_dist=100) # Change the max dist parameter as appropriate for your DEM
            raster = self.wbe.fill_depressions(self.dem_clipped_burned_raster, flat_increment=0.001)
            raster = self.save_raster(raster, Names.demFilledName, True, True)

        return raster

#endregion
    
#region farm & field

    # def __remove_non_agriculture_cell(self, raster:Raster)->Raster:
    #     """
    #     remove non agriculture cells

    #     Replace filterAgriLanduse
    #     """
    #     raster_with_only_algriculture = raster.farm_raster.deep_copy()
    #     algricultrual_landuses = self.parameter.bmp_database.algricultural_landuses

    #     for row in raster.configs.rows:
    #         for col in raster.configs.columns:
    #             landuse = self.mapped_landuse_raster[row, col]
                
    #             if landuse > 0 and landuse not in algricultrual_landuses:
    #                 raster_with_only_algriculture[row, col] = raster.configs.nodata

    #     return raster_with_only_algriculture

    @property
    def farm_raster(self)->Raster:
        raster = self.get_raster(Names.farmRasName)
    
        if raster is None:
            if self.inputs.is_farm_same_as_field:
                raster = self.save_raster(self.field_raster, Names.farmRasName, True, True)
            elif self.inputs.farm_vector is not None:
                exist, id_field_name = VectorExtension.check_id(self.inputs.farm_vector)
                if not exist:
                    raise ValueError(f"Couldn't find ID column in {self.inputs.farm_vector.file_name} ...")
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.farm_vector, 
                                                            field_name = id_field_name,
                                                            base_raster = self.inputs.dem_raster)
                raster = self.mask_refined_with_subbasin_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, raster)
                raster = self.save_raster(raster, Names.farmRasName, True, True)

        return raster
    
    # @property
    # def farm_without_agriculture_raster(self)->Raster:
    #     raster = self.get_raster(Names.farmWithOnlyAgricultureRasName)

    #     if raster is None:
    #         raster = self.__remove_non_agriculture_cell(self.farm_raster)
    #         raster = self.mask_refined_with_subbasin_raster.con("value == 1", raster, raster.configs.nodata)
    #         self.save_raster(raster, Names.farmWithOnlyAgricultureRasName)

    #     return raster

    
    @property
    def field_raster(self)->Raster:
        raster = self.get_raster(Names.fieldRasName)
    
        if raster is None:
            if self.inputs.field_vector is not None:
                exist, id_field_name = VectorExtension.check_id(self.inputs.field_vector)
                if not exist:
                    raise ValueError(f"Couldn't find ID column in {self.inputs.field_vector.file_name} ...")
                raster = self.wbe.vector_polygons_to_raster(
                    input = self.inputs.field_vector, 
                    field_name = id_field_name,
                    base_raster = self.inputs.dem_raster)
                raster = self.mask_refined_with_subbasin_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, raster)
                raster = self.save_raster(raster, Names.fieldRasName, True, True)

        return raster
    
    @property
    def field_clipped_vector(self)->Vector:
        """Clipped field vector by subbasin"""
        vector = self.get_vector(Names.fieldClippedShpName)

        if vector is None:
            if self.field_raster is not None:
                vector = RasterExtension.raster_to_vector(self.field_raster)
                self.save_vector(vector, Names.fieldClippedShpName)

        return vector

        
    
    # @property
    # def field_without_agriculture_raster(self)->Raster:
    #     raster = self.get_raster(Names.fieldWithOnlyAgricultureRasName)

    #     if raster is None:
    #         raster = self.__remove_non_agriculture_cell(self.field_raster)
    #         raster = self.mask_refined_with_subbasin_raster.con("value == 1", raster, raster.configs.nodata)
    #         self.save_raster(raster, Names.fieldWithOnlyAgricultureRasName)

    #     return raster

#endregion    

#region parameters

    @property
    def mapped_soil_raster(self)->Raster:
        """
        mapped soil raster based on lookup table
        The name must be soil as specified in the engine
        """
        raster = self.get_raster(Names.soilName)

        if raster is None:
            raster = self.inputs.lookup_soil.mapped_raster
            raster = self.save_raster(raster, Names.soilName, True, True)

        return raster
    
    @property
    def soil_k_raster(self)->Raster:
        return RasterExtension.reclassify(self.mapped_soil_raster, self.parameter.get_parameter_lookup("AverageK","soil"), self.subbasin_raster)

    @property
    def soil_porosity_raster(self)->Raster:
        return RasterExtension.reclassify(self.mapped_soil_raster, self.parameter.get_parameter_lookup("AveragePorosity","soil"), self.subbasin_raster)

    @property
    def landuse_rootdepth_raster(self)->Raster:
        return RasterExtension.reclassify(self.mapped_landuse_raster, self.parameter.get_parameter_lookup("ROOT_DEPTH","landuse"), self.subbasin_raster)

    @property
    def mapped_landuse_raster(self)->Raster:
        """
        mapped landuse raster based on lookup table. 
        The name must be landuse as specified in the engine
        """
        raster = self.get_raster(Names.landuseName)

        if raster is None:
            raster = self.inputs.lookup_landuse.mapped_raster
            raster = self.save_raster(raster, Names.landuseName, True, True)

        return raster

    @property
    def uslep_raster(self)->Raster:
        """
        use default usle P as 1, just copy from the mask
        """
        raster = self.get_raster(Names.uslePName)
        if raster is None:
            logger.info("Creating USLE P raster ...")
            self.save_raster(self.mask_refined_with_subbasin_raster, Names.uslePName)
            raster = self.get_raster(Names.uslePName)

        return raster

    @property
    def field_capacity_raster(self)->Raster:
        """
        field capacity from soil and soil parameter table in parameter database
        """
        raster = self.get_raster(Names.fieldCapName)
        if raster is None:
            raster = RasterExtension.reclassify(self.mapped_soil_raster, self.parameter.get_parameter_lookup("FC1","soil"), self.subbasin_raster)
            raster = self.save_raster(raster, Names.fieldCapName, True, True)      

        return raster
    
    @property
    def manning_raster(self)->Raster:
        """
        manning from landuse and landuse parameter table in parameter database
        """
        raster = self.get_raster(Names.manningName)
        if raster is None:
            raster = RasterExtension.reclassify(self.mapped_landuse_raster, self.parameter.get_parameter_lookup("MANNING","landuse"), self.subbasin_raster)
            raster = self.save_raster(raster, Names.manningName, True, True)

        return raster
    
    @property
    def velocity_raster(self)->Raster:
        """
        velocity, need verify
        """
        raster = self.get_raster(Names.velocityName)

        if raster is None:
            min = 0.005
            max = 3
            velocity = self.slope_radius_raster.sqrt() * self.reach_depth_raster**0.6667 / self.manning_raster
            velocity = self.subbasin_raster.con("value > 0", velocity, velocity.configs.nodata)
            raster = velocity.min(max).max(min)
            raster = self.save_raster(raster, Names.velocityName, True, True)
        return raster
           
    @property
    def wetness_index_raster(self)->Raster:
        """
        wetness index
        """
        raster = self.get_raster(Names.wetnessIndexName)

        if raster is None:
            raster = (self.flow_acc_raster * self.inputs.cellsize_m2 / self.slope_radius_raster).ln()
            raster = self.subbasin_raster.con("value > 0", raster, raster.configs.nodata)
            raster = self.save_raster(raster, Names.wetnessIndexName, True, True)

        return raster
    
    @property
    def initial_soil_moisture_raster(self)->Raster:
        """
        initial soil moisture interpolated based on wetness index
        """

        raster = self.get_raster(Names.moistureInitialName)

        if raster is None:
            minSaturation = 0.05 
            maxSaturation = 1

            minWetnessIndex = self.wetness_index_raster.configs.minimum
            maxWetnessIndex = self.wetness_index_raster.configs.maximum * 0.8

            wti = self.wetness_index_raster.min(maxWetnessIndex)
            ratio = (wti - minWetnessIndex) * (maxSaturation - minSaturation) / (maxWetnessIndex - minWetnessIndex) + minSaturation
            raster = ratio * self.field_capacity_raster
            raster = self.subbasin_raster.con(f"value == {self.subbasin_raster.configs.nodata}", raster.configs.nodata, raster)

            raster = self.save_raster(raster, Names.moistureInitialName, True, True)
        return raster
    
    @property
    def potential_ruoff_coefficient_raster(self)->Raster:
        """
        potential runoff coefficient
        """

        raster = self.get_raster(Names.PRCName)
        subbasin_nodata = self.subbasin_raster.configs.nodata

        if raster is None:
            slope_raster = self.slope_degree_raster
            soil_raster = self.mapped_soil_raster
            landuse_raster = self.mapped_landuse_raster
            flow_dir_raster = self.flow_direction_raster
            reach_raster = self.reach_raster
            reach_width_raster = self.reach_width_raster
            raster = self.inputs.create_new_raster()

            for row in range(self.inputs.rows):
                for col in range(self.inputs.columns):
                    if self.subbasin_raster[row, col] == subbasin_nodata:
                        continue
                    slope = slope_raster[row, col]
                    landuse = landuse_raster[row, col]
                    soil = soil_raster[row,col]
                    reach = reach_raster[row,col]
                    reach_width = reach_width_raster[row,col]
                    flow_dir = flow_dir_raster[row,col]

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    raster[row,col] = self.parameter.get_potential_runoff_coefficient(landuse, soil, slope, reachWaterSurfaceFraction)
           
            raster = self.save_raster(raster, Names.PRCName, True, True)

        return raster
    
    @property
    def potential_ruoff_coefficient_accumulate_average_raster(self)->Raster:
        """
        accumulative potential runoff coefficient
        """

        raster = self.get_raster(Names.PRCAccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.potential_ruoff_coefficient_raster)

            raster = self.save_raster(raster, Names.PRCAccAvgName, True, True)
        return raster
    
    @property
    def depression_storage_capacity_raster(self)->Raster:
        """
        depression storage
        """
        raster = self.get_raster(Names.DSCName)

        subbasin_nodata = self.subbasin_raster.configs.nodata

        if raster is None:
            slope_raster = self.slope_degree_raster
            soil_raster = self.mapped_soil_raster
            landuse_raster = self.mapped_landuse_raster
            flow_dir_raster = self.flow_direction_raster
            reach_raster = self.reach_raster
            reach_width_raster = self.reach_width_raster
            raster = self.inputs.create_new_raster()

            for row in range(self.inputs.rows):
                for col in range(self.inputs.columns):
                    if self.subbasin_raster[row, col] == subbasin_nodata:
                        continue
                    slope = slope_raster[row, col]
                    landuse = landuse_raster[row, col]
                    soil = soil_raster[row,col]
                    reach = reach_raster[row,col]
                    reach_width = reach_width_raster[row,col]
                    flow_dir = flow_dir_raster[row,col]

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    raster[row,col] = self.parameter.get_depression_storage_capacity(
                        landuse, soil, slope, reachWaterSurfaceFraction)
           
            raster = self.save_raster(raster, Names.DSCName, True, True)

        return raster
    
    @property
    def depression_storage_capacity_accumulate_average_raster(self)->Raster:
        """
        depresion storage accumulative
        """

        raster = self.get_raster(Names.DSCAccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.depression_storage_capacity_raster)

            raster = self.save_raster(raster, Names.DSCAccAvgName, True, True)
        return raster
    
    @property
    def cn2_raster(self)->Raster:
        """
        CN2 parameter
        """

        raster = self.get_raster(Names.cn2Name)
        subbasin_nodata = self.subbasin_raster.configs.nodata
        if raster is None:
            slope_raster = self.slope_degree_raster
            soil_raster = self.mapped_soil_raster
            landuse_raster = self.mapped_landuse_raster
            flow_dir_raster = self.flow_direction_raster
            reach_raster = self.reach_raster
            reach_width_raster = self.reach_width_raster
            raster = self.inputs.create_new_raster()

            for row in range(self.inputs.rows):
                for col in range(self.inputs.columns):
                    slope = slope_raster[row, col]
                    landuse = landuse_raster[row, col]
                    soil = soil_raster[row,col]
                    reach = reach_raster[row,col]
                    reach_width = reach_width_raster[row,col]
                    flow_dir = flow_dir_raster[row,col]
                    if self.subbasin_raster[row, col] == subbasin_nodata:
                        continue

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    cn2 = self.parameter.get_cn2(landuse, soil)
                    if reachWaterSurfaceFraction > 0:  # stream
                        cn2 = reachWaterSurfaceFraction * 100.0 + (1 - reachWaterSurfaceFraction) * cn2
                        cn2 = max(cn2, 35.0)
                        cn2 = min(cn2, 100.0)

                    raster[row,col] = cn2
           
            raster = self.save_raster(raster, Names.cn2Name, True, True)

        return raster
    
    @property
    def cn2_accumulate_average_raster(self)->Raster:
        raster = self.get_raster(Names.Cn2AccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.cn2_raster)

            raster = self.save_raster(raster, Names.Cn2AccAvgName, True, True)
        return raster
    
    def __calculate_reach_water_surface_fraction(self, reach, reach_width, flow_dir):
        reachWaterSurfaceFraction = 0.0
        if reach > 0:
            if flow_dir in [1, 4, 16, 64]:  # corner direction
                reachWaterSurfaceFraction = reach_width / self.inputs.cell_size
                reachWaterSurfaceFraction = 1.41421356 * reachWaterSurfaceFraction - 0.5 * reachWaterSurfaceFraction * reachWaterSurfaceFraction
            else:
                reachWaterSurfaceFraction = reach_width / self.inputs.cell_size
        
            reachWaterSurfaceFraction = max(0.0, reachWaterSurfaceFraction)
            reachWaterSurfaceFraction = min(1.0, reachWaterSurfaceFraction)     
        return reachWaterSurfaceFraction      

    def __value_accumulate_d8(self, input_raster:Raster, is_average:bool = True)->Raster:
        row, col, x, y = 0, 0, 0, 0
        z, z2 = 0.0, 0.0
        v, v2 = 0.0, 0.0
        i = 0
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        inflowingVals = [16, 32, 64, 128, 1, 2, 4, 8]
        numInNeighbours = 0.0
        isAvg = False
        flag = False
        flowDir = 0.0

        isAvg = is_average

        try:
            pntr = self.flow_direction_raster
            valueRas = input_raster

            noData = pntr.configs.nodata
            rows = pntr.configs.rows
            cols = pntr.configs.columns
    
            output = self.inputs.create_new_raster
            temp = np.full((rows, cols), 1.0)

            tmpGrid1 = self.inputs.create_new_raster

            for row in range(rows):
                for col in range(cols):
                    if pntr[row, col] != noData and valueRas[row, col] != noData:
                        z = 0
                        for i in range(8):
                            if pntr[row + dY[i], col + dX[i]] == inflowingVals[i]:
                                z += 1
                        tmpGrid1[row, col] = z
                        output[row, col] = valueRas[row, col]
                    else:
                        temp[row, col] = noData

            for row in range(rows):
                for col in range(cols):
                    if tmpGrid1[row, col] == 0:
                        tmpGrid1[row, col] = -1
                        x, y = col, row
                        while True:
                            z = temp[y, x]
                            v = output[y, x]
                            flowDir = pntr[y, x]
                            if flowDir > 0:
                                i = int(math.log(flowDir) / math.log(2))
                                x += dX[i]
                                y += dY[i]
                                z2 = temp[y, x]
                                temp[y, x] = z2 + z
                                v2 = output[y, x]
                                output[y, x] = v2 + v
                                numInNeighbours = tmpGrid1[y, x] - 1
                                tmpGrid1[y, x] = numInNeighbours
                                if numInNeighbours == 0:
                                    tmpGrid1[y, x] = -1
                                    flag = True
                                else:
                                    flag = False
                            else:
                                flag = False
                            if not flag:
                                break

            if isAvg:
                for row in range(rows):
                    for col in range(cols):
                        flowDir = output[row, col]
                        if flowDir != noData and valueRas[row, col] != noData:
                            output[row, col] = output[row, col] / temp[row, col]
                        else:
                            output[row, col] = noData

            return output

        except MemoryError:
            print("memory error")
        except Exception as e:
            print(e)
        finally:
            pass
    
#endregion

#region delineation

    @property
    def flow_direction_no_changed_raster(self)->Raster:
        """Flow direction based on the filled dem. No further modifications are applied."""
        flow_dir_raster = self.get_raster(Names.flowDirD8NoChangeName)     

        if flow_dir_raster is None:
            flow_dir_raster = self.wbe.d8_pointer(dem = self.dem_clipped_burned_filled_raster)
            flow_dir_raster = self.save_raster(flow_dir_raster,Names.flowDirD8NoChangeName, True, True)

        return flow_dir_raster

    @property
    def flow_direction_raster(self)->Raster:
        """Flow direction modified by structures"""
        flow_dir_raster = self.get_raster(Names.flowDirD8Name)     

        if flow_dir_raster is None:
            if self.structure_combined is not None:                
                #if there are some structure, use the structure to get the flow direction
                #merge all structure boundary and outlets to get the final flow direction.
                flow_dir_raster = self.flow_direction_no_changed_raster
                flow_dir_raster = self.structure_combined.generate_flow_direction_raster_shawn()
            else:
                #if there are no structure, use the dem directly
                logger.info("Creating flow direction based on dem ...")
                flow_dir_raster = self.wbe.d8_pointer(dem = self.dem_clipped_burned_filled_raster)
            flow_dir_raster = self.save_raster(flow_dir_raster, Names.flowDirD8Name, True, True)
        
        return flow_dir_raster

    @property
    def flow_acc_raster(self)->Raster:
        """Flow accumulation raster"""
        raster = self.get_raster(Names.flowAccName)

        if raster is None:  
            logger.info("Creating flow accumulation raster ...")
            raster = self.wbe.d8_flow_accum(raster = self.flow_direction_raster, 
                                            input_is_pointer = True,
                                            out_type='cells')
            raster = self.save_raster(raster, Names.flowAccName, True, True)

        return raster
    
    @property
    def flow_length_raster(self)->Raster:        
        raster = self.get_raster(Names.flowLengthName)

        if raster is None:
            logger.info("Creating flow length raster ...")
            raster = Delineation.get_flow_path_length(self.flow_direction_no_changed_raster, self.dem_clipped_raster_for_model)
            raster = self.save_raster(raster, Names.flowLengthName, True, True)

        return raster    
    
    @property
    def stream_network_user_raster(self)->Raster:
        """stream network provided by user for burn-in"""
        raster = self.get_raster(Names.streamNetworUserRasName)        
        if raster is None:
            raster = self.wbe.vector_lines_to_raster(
                input = self.inputs.stream_network_user_vector, 
                base_raster = self.inputs.dem_raster)
            #raster = self.wbe.buffer_raster(raster, self.inputs.cell_size)
            raster = self.save_raster(raster, Names.streamNetworUserRasName, True, True)
        return raster
    
    @property
    def stream_main_raster(self)->Raster:
        """stream network delineated with fixed 200ha threshold to define the pour points."""

        raster = self.get_raster(Names.streamMainRasName)
   
        if raster is None:       
            #get streams from the flow accumuation 
            logger.info(f"Extracting stream raster with threashold area of {self.main_stream_threshold_area_ha}ha ...")    
            raster = self.wbe.extract_streams(
                flow_accumulation = self.flow_acc_raster, 
                threshold = self.main_stream_threshold_area_ha / self.inputs.cellsize_ha)
                 
            #save it
            raster = self.save_raster(raster, Names.streamMainRasName, True, True)

        return raster   

    @property
    def stream_network_raster(self)->Raster:
        """stream network delineated with user defined threshold. The structures are also considered."""

        raster = self.get_raster(Names.streamNetworkRasName)
   
        if raster is None:       
            #get streams from the flow accumuation 
            logger.info(f"Extracting stream raster with threashold area of {self.stream_threshold_area_ha}ha ...")    
            raster = self.wbe.extract_streams(
                flow_accumulation = self.flow_acc_raster, 
                threshold = self.stream_threshold_area_ha / self.inputs.cellsize_ha)
            
            #fix it as some of the structure streams may be below the threshold 
            if len(self.structures) > 0:
                logger.info("Fixing stream network so the structure stream segment that is below threashold will be added back ...")
                raster = Delineation.build_stream_network_link_to_outlets(raster, self.flow_direction_raster,self.structure_combined_outlet_raster)
            #we also do it for wacob
            if self.inputs.wascob_vector is not None:
                wascob_raster = VectorExtension.vector_to_raster(self.inputs.wascob_vector, self.dem_clipped_raster)
                raster = Delineation.build_stream_network_link_to_outlets(raster, self.flow_direction_raster,wascob_raster)

            #save it
            raster = self.save_raster(raster, Names.streamNetworkRasName, True, True)

        return raster    
    
    @property
    def stream_network_vector(self)->Vector:
        vector = self.get_vector(Names.streamNetworkShpName)
   
        if vector is None:            
            vector = self.wbe.raster_streams_to_vector(streams = self.stream_network_raster, d8_pointer = self.flow_direction_raster)
            self.save_vector(vector, Names.streamNetworkRasName)

        return vector    
    
    @property
    def stream_pour_point_raster(self)->Raster:
        """
        the raster of all stream outlets
        """
        raster = self.get_raster(Names.streamPourPointRasName)

        if raster is None:
            logger.info("Converting stream outlets pour point vector to raster ...")
            raster = self.wbe.vector_points_to_raster(input = self.stream_pour_points_vector,
                                                      base_raster = self.inputs.dem_raster)
            raster = self.save_raster(raster, Names.streamPourPointRasName, True, True)

        return raster

    @property
    def stream_pour_points_vector(self)->Vector:
        """
        the stream outlets considering structures, user-defined outlets and reservoirs
        """
        vector = self.get_vector(Names.streamPourPointShpName)

        if vector is None:
            logger.info("Merging all possible stream outlets pour points to a single vector ...")

            #merge the pour points and user-provided reservoir and outlets
            outlet_vectors = []

            #add stream outlets delineated using main stream
            logger.info("Creating pour points with main stream (200ha threshold) ...")
            pour_points_vector = Delineation.get_pour_points(
                self.stream_main_raster, 
                self.flow_direction_raster, 
                [structure.boundary_raster for structure in self.structures.values()])
            outlet_vectors.append(pour_points_vector)
            
            #add user-defined subbasin outlets and snap it to the stream network
            if self.inputs.outlet_vector is not None:
                outlet_vectors.append(self.wbe.jenson_snap_pour_points(
                    pour_pts = self.inputs.outlet_vector,
                    streams = self.stream_network_raster,
                    snap_dist = 2000))

            #add reach bmp points but exclude wetland
            for reach_bmp in self.inputs.reach_bmp_vectors:
                if reach_bmp is not None:
                    outlet_vectors.append(self.wbe.jenson_snap_pour_points(
                        pour_pts = reach_bmp,
                        streams = self.stream_network_raster,
                        snap_dist = 2000))
                    
            #add user-defined tile drain outlets
            if self.tile_drain_outlet_pour_points_vector is not None:
                outlet_vectors.append(self.tile_drain_outlet_pour_points_vector)
                
            #add wascob points
            if self.inputs.wascob_vector is not None:
                outlet_vectors.append(self.wbe.jenson_snap_pour_points(
                    pour_pts = self.inputs.wascob_vector,
                    streams = self.stream_network_raster,
                    snap_dist = 2000))

            #add structure outlets
            #there is no need to snap as the outlet has been processed with the network
            if len(self.structures) > 0:
                outlet_vectors.extend([structure.outlet_vector for structure in self.structures.values()])

            vector = VectorExtension.merge_vectors(outlet_vectors)
            self.save_vector(vector, Names.streamPourPointShpName)

        return vector

    @property
    def subbasin_vector(self)->Vector:
        vector = self.get_vector(Names.subbasinShpName)

        if vector is None:
            vector = RasterExtension.raster_to_vector(self.subbasin_raster)
            self.save_vector(vector, Names.subbasinShpName)

        return vector

    @property
    def subbasin_raster(self)->Raster:
        raster = self.get_raster(Names.subbasinRasName)

        if raster is None:
            #get subbasins
            logger.info("creating subbasins ...")
            raster = self.wbe.watershed(
                d8_pointer=self.flow_direction_raster, 
                pour_points=self.stream_pour_points_vector)

            #reorder the subbasin starting from 1
            logger.info("Reordering subbasin ...")
            Delineation.reorder_raster_id(raster)

            #fix the subbasins considering the structures
            logger.info("Fixing subbasin for structure and assign subbasin id to sturcture ...")
            for type,structure in self.structures.items():
                #logger.info(type)
                structure.repair_subbasin_and_assign_subbasin_id_contribution_area_to_sturcture(raster, self.flow_acc_raster)  

            #save the subbasin raster
            raster = self.save_raster(raster, Names.subbasinRasName, True, True)

        return raster
    
    @property
    def slope_percent_raster(self)->Raster:
        raster = self.get_raster(Names.slopePercentName)

        if raster is None:
            logger.info("creating slope (percent) raster ...")
            raster = self.slope_radius_raster * 100
            raster = self.save_raster(raster, Names.slopePercentName, True, True)

        return raster
    
    @property
    def slope_radius_raster(self)->Raster:
        raster = self.get_raster(Names.slopeRadiusName)

        if raster is None:
            logger.info("creating slope (radius) raster ...")
            raster = (self.slope_degree_raster * math.pi / 180).tan()
            raster = self.save_raster(raster, Names.slopeRadiusName, True, True)

        return raster
    
    @property
    def slope_degree_raster(self)->Raster:        
        raster = self.get_raster(Names.slopeDegName)

        if raster is None:
            logger.info("creating slope (degree) raster ...")
            raster = self.wbe.slope(dem = self.dem_clipped_burned_filled_raster)
            raster = self.save_raster(raster, Names.slopeDegName, True, True)

        return raster

    @property
    def stream_order_raster(self)->Raster:
        raster = self.get_raster(Names.streamOrderRasName)  

        if raster is None:
            logger.info("creating stream order raster ...")
            raster = self.wbe.strahler_stream_order(d8_pntr = self.flow_direction_raster, streams_raster = self.stream_network_raster)
            raster = self.save_raster(raster, Names.streamOrderRasName, True, True)

        return raster
            

#endregion

#region reach

    @property
    def reach_vector(self)->Vector:
        vector = self.get_vector(Names.reachShpName) 

        if vector is None:
            logger.info("creating reach vector ...")
            vector = self.wbe.raster_streams_to_vector(streams = self.reach_raster, d8_pointer = self.flow_direction_raster)
            self.save_vector(vector, Names.reachShpName)

        return vector

    @property
    def reach_raster(self)->Raster:
        raster = self.get_raster(Names.reachRasName) 

        if raster is None:
            logger.info("creating reach raster ...")
            raster = self.stream_network_raster.con("value >= 0", self.subbasin_raster, self.subbasin_raster.configs.nodata)
            raster = self.save_raster(raster, Names.reachRasName, True, True)

        return raster

    @property
    def reach_width_raster(self)->Raster:
        """
        calculate reach width for 2-year design storm, will use-defined parameter later
        """
        return self._get_reach_width_depth_raster(False)
    
    @property
    def reach_depth_raster(self)->Raster:
        """
        calculate reach depth for 2-year design storm, will use-defined parameter later
        """
        return self._get_reach_width_depth_raster(True)
    
    def _get_reach_width_depth_raster(self, isdepth:bool)->Raster:
        """
        calculate reach width/depth raster using given design storm

        replace StreamWidth and StreamDepth
        """
        file_name = Names.reachWidthName
        if isdepth:
            file_name = Names.reachDepthName

        raster = self.get_raster(file_name)
        if raster is None:
            
            logger.info(f"creating reach {"depth" if isdepth else "width"} raster ...")
            parameter = self.parameter.get_reach_width_parameter(self.design_storm_return_period)          
            if isdepth:
                parameter = self.parameter.get_reach_depth_parameter(self.design_storm_return_period) 
            raster = (self.flow_acc_raster * self.inputs.cellsize_km2 * parameter.A) ** parameter.B
            raster = self.stream_network_raster.con("value > 0", raster, raster.configs.nodata)
            raster = self.save_raster(raster, file_name, True, True)

        return raster

    @property
    def reach_parameter_df(self)->pd.DataFrame:
        df = self.get_df(Names.reachParameterCsvName)

        if df is None:            
            df = Reach(self.dem_clipped_raster, 
                       self.subbasin_raster,
                       self.stream_network_raster,
                       self.stream_order_raster,
                       self.flow_length_raster,
                       self.flow_direction_raster,
                       self.flow_acc_raster,
                       self.reach_width_raster,
                       self.reach_depth_raster,
                       self.velocity_raster
                       ).reach_parameter_df 
            self.save_df(df, Names.reachParameterCsvName)

        return df  

#endregion

#region bmps

    @property
    def marginal_crop_land_raster(self):
        """
        generate marginal crop land

        replace MarginalCropland
        """
        raster = self.get_raster(Names.marCroplandRasName)  

        if raster is None and self.marginal_crop_land_landuse_ids is not None and len(self.marginal_crop_land_landuse_ids) > 0:
            filtered_landuse_raster = RasterExtension.filter_by_values(self.mapped_landuse_raster, self.marginal_crop_land_landuse_ids)
            buffered_landuser_raster = self.wbe.buffer_raster(input = filtered_landuse_raster, buffer_size = self.marginal_crop_land_buffer_size_m) #need test

            slope_threshod_deg = max(math.atan(self.marginal_crop_land_slope_threshod / 100) * 180.0 / math.pi, 0.0)
            
            raster = self.field_without_agriculture_raster.deep_copy()
            raster = buffered_landuser_raster.con("value > 0", raster, raster.configs.nodata)
            raster = self.slope_degree_raster.con(f"value >= {slope_threshod_deg}", raster, raster.configs.nodata)    
            raster = self.mask_refined_with_subbasin_raster.con(f"value > 0", raster, raster.configs.nodata)

            raster = self.save_raster(raster, Names.marCroplandRasName, True, True)
                    
        return raster
    
    @property
    def pasture_land_raster(self):
        """
        generate pasture land

        replace BuildMapOnLandUse
        """
        raster = self.get_raster(Names.pastureLandRasName)  

        if raster is None and self.pasture_land_landuse_ids is not None and len(self.pasture_land_landuse_ids) > 0:
            filtered_landuse_raster = RasterExtension.filter_by_values(self.mapped_landuse_raster, self.pasture_land_landuse_ids)
            
            raster = self.field_without_agriculture_raster.deep_copy()
            raster = filtered_landuse_raster.con("value > 0", raster, raster.configs.nodata)
            raster = self.mask_refined_with_subbasin_raster.con(f"value > 0", raster, raster.configs.nodata)

            raster = self.save_raster(raster, Names.pastureLandRasName, True, True)
                    
        return raster

#region Riparian Buffer

    @property
    def riparian_buffer_raster(self)->Raster:
        raster = self.get_raster(Names.riparianBufferRasterName)
    
        if raster is None:
            if self.inputs.raparian_buffer_vector is not None:
                exist, id_field_name = VectorExtension.check_id(self.inputs.raparian_buffer_vector)
                if not exist:
                    raise ValueError(f"Couldn't find ID column in {self.inputs.raparian_buffer_vector.file_name} ...")
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.raparian_buffer_vector, 
                                                            field_name = id_field_name,
                                                            base_raster = self.inputs.dem_raster)
                raster = self.mask_refined_with_subbasin_raster.con(f"value == {self.inputs.nodata}", self.inputs.nodata, raster)
                raster = self.save_raster(raster, Names.riparianBufferRasterName, True, True)

        return raster
    
    @property
    def riparian_buffer_drainage_area_raster(self)->Raster:
        raster = self.get_raster(Names.riparianBufferDrainageRasterName)

        if raster is None:
            self.__create_riparian_buffer_distribution_paramter()
            raster = self.get_raster(Names.riparianBufferDrainageRasterName)

        return raster

    @property
    def riparian_buffer_parts_raster(self)->Raster:
        raster = self.get_raster(Names.riparianBufferPartRasterName)

        if raster is None:
            self.__create_riparian_buffer_distribution_paramter()
            raster = self.get_raster(Names.riparianBufferPartRasterName)

        return raster   
    
    @property
    def riparian_buffer_parameter_df(self)->pd.DataFrame:
        df = self.get_df(Names.riparianBufferParameterCSVName)

        if df is None:
            self.__create_riparian_buffer_distribution_paramter()
            df = self.get_df(Names.riparianBufferParameterCSVName)

        return df  

    def __create_riparian_buffer_distribution_paramter(self, width = 10):
        """
        create distribution raster and parameter table for riparian buffer. 
        
        It finds all parts of the buffer in each subbasin and corresponding drainage area. And then summarize the paramters. 

        Replace Plugin VFSandRBS
        """

        row, col, x, y = 0, 0, 0, 0
        z = 0.0
        i, c = 0, 0
        flag = False
        flowDir = 0.0

        if self.riparian_buffer_raster is None:
            return

        logger.info("Creating riparian buffer distribution and parameters ... ")

        rows = self.flow_direction_raster.configs.rows
        cols = self.flow_direction_raster.configs.columns
        riparian_buffer_nodata = self.riparian_buffer_raster.configs.nodata
        subbasin_nodata = self.subbasin_raster.configs.nodata

        riparian_buffer_drainage_area_raster = self.wbe.new_raster(self.subbasin_raster.configs)
        riparian_buffer_parts_raster = self.wbe.new_raster(self.subbasin_raster.configs)

        #flag if the cells has been traced
        flag2D = np.zeros((rows, cols), dtype=bool)


        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        LnOf2 = 0.693147180559945
        path = []
        pathInside = []
        vfsOrRbsDrain = {}
        vfsOrRbsInside = {}
        vfsOrRbsLength = {}
        celldist = (self.riparian_buffer_raster.configs.resolution_x + self.riparian_buffer_raster.configs.resolution_y) / 2.0

        for row in range(rows):
            for col in range(cols):
                if self.subbasin_raster[row, col] != subbasin_nodata and not flag2D[row, col]:
                    path = []
                    pathInside = []

                    x = col
                    y = row

                    path.append((y, x))

                    flag = True
                    length = 0.0

                    while flag:
                        flowDir = self.flow_direction_raster[y, x]
                        if flowDir > 0:
                            c = int(math.log(flowDir) / LnOf2)

                            lastVFSorRBSID = self.riparian_buffer_raster[y, x]
                            isVisited = flag2D[y, x]

                            if lastVFSorRBSID != riparian_buffer_nodata and not isVisited:
                                pathInside.append((y, x))
                                length += celldist * (1.41421356 if c in [1, 4, 16, 64] else 1)

                            #get x,y for downstream cell
                            x += dX[c]
                            y += dY[c]

                            #check to see if the next cell is edge, different riparian buffer. If yes, add it to the list
                            if (self.riparian_buffer_raster[y, x] == riparian_buffer_nodata 
                                or self.riparian_buffer_raster[y, x] != lastVFSorRBSID 
                                or self.flow_direction_raster[y, x] == 0) and lastVFSorRBSID != riparian_buffer_nodata:
                                #recalculate the current position
                                loc = (y - dY[c], x - dX[c])

                                if loc in vfsOrRbsDrain:
                                    vfsOrRbsDrain[loc].extend(path)
                                else:
                                    vfsOrRbsDrain[loc] = path.copy()

                                if loc in vfsOrRbsInside:
                                    vfsOrRbsInside[loc].extend(pathInside)
                                else:
                                    vfsOrRbsInside[loc] = pathInside.copy()

                                if loc in vfsOrRbsLength:
                                    vfsOrRbsLength[loc] = max(length, vfsOrRbsLength[loc])
                                else:
                                    vfsOrRbsLength[loc] = length
                                break

                            if not isVisited:
                                path.append((y, x))
                        else:
                            flag = False

                    #update the flag
                    for loc in path:
                        flag2D[loc[0], loc[1]] = True

        #create the resulting parameter dictionary
        riparain_buffer_parameter_df = pd.DataFrame(columns=['ID','RIBUF_ID','Subbasin','Area_ha','Drainage_Area','Area_Ratio','Length'])
        riparain_buffer_parameter_df.set_index('ID', inplace=True)        

        cellArea = self.riparian_buffer_raster.configs.resolution_x * self.riparian_buffer_raster.configs.resolution_y
        vfsOrRbsPartID = 0
        for outLoc in vfsOrRbsDrain.keys():
            vfsOrRbsPartID += 1

            vfsOrRbsID = int(self.riparian_buffer_raster[outLoc[0], outLoc[1]])
            subID = int(self.subbasin_raster[outLoc[0], outLoc[1]])
            drainageArea = len(vfsOrRbsDrain[outLoc]) * cellArea / 10000
            length = vfsOrRbsLength[outLoc]

            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'RIBUF_ID'] = vfsOrRbsID
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Subbasin'] = subID
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Drainage_Area'] = drainageArea
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Length'] = length

            for loc in vfsOrRbsDrain[outLoc]:
                riparian_buffer_drainage_area_raster[loc[0], loc[1]] = vfsOrRbsPartID

            for loc in vfsOrRbsInside[outLoc]:
                riparian_buffer_parts_raster[loc[0], loc[1]] = vfsOrRbsPartID

        riparain_buffer_parameter_df["Width"] = width
        riparain_buffer_parameter_df["Area_ha"] = width * riparain_buffer_parameter_df['Length'] * 0.0001
        riparain_buffer_parameter_df["Area_Ratio"] = riparain_buffer_parameter_df["Drainage_Area"] / riparain_buffer_parameter_df["Area_ha"]
        riparain_buffer_parameter_df["VegetationID"] = 6

        #get slope, soil_k, soil_porosity and root_depth using the zone statistics
        slope_df = RasterExtension.get_zonal_statistics(self.slope_degree_raster, riparian_buffer_parts_raster, "mean","Slope")
        k_df = RasterExtension.get_zonal_statistics(self.soil_k_raster, riparian_buffer_parts_raster, "mean","Sol_K")
        prosity_df = RasterExtension.get_zonal_statistics(self.soil_porosity_raster, riparian_buffer_parts_raster, "mean","Sol_porosity")
        root_depth_df = RasterExtension.get_zonal_statistics(self.landuse_rootdepth_raster, riparian_buffer_parts_raster, "mean","Root_Depth")

        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(slope_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(k_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(prosity_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(root_depth_df, left_index=True, right_index=True, how="inner")

        #add other columns with default values
        riparain_buffer_parameter_df["Scenario"] = DefaultScenarioId
        riparain_buffer_parameter_df["Year"] = 0

        #adjust the sequence of the columns
        riparain_buffer_parameter_df.reset_index(inplace=True)
        riparain_buffer_parameter_df = riparain_buffer_parameter_df[['Scenario','ID','Year','RIBUF_ID','Subbasin','VegetationID','Length','Width','Area_ha','Drainage_Area','Area_Ratio','Slope','Sol_K','Sol_porosity','Root_Depth']]

        #save to bmp database
        self.save_raster(riparian_buffer_drainage_area_raster, Names.riparianBufferDrainageRasterName)
        self.save_raster(riparian_buffer_parts_raster, Names.riparianBufferPartRasterName)
        self.save_df(riparain_buffer_parameter_df, Names.riparianBufferParameterCSVName)

#endregion

#endregion

#region interpolation

#endregion

#region iuh

    def __create_iuh_rasters(self):
        logger.info("Generating IUH rasters ... ")
        max_min_v = self.parameter.parameter_database.iuh_max_min_v        

        iuh = IUH(self.dem_clipped_raster_for_model, self.slope_percent_raster,
                  self.flow_direction_raster, self.flow_acc_raster, self.manning_raster,self.stream_network_raster)
        
        #2yr
        logger.info("2 yr ...")
        radius_parameter = self.parameter.parameter_database.iuh_2yr
        iuh_2yr = iuh.generate_travel_time_average_standard_deviation(radius_parameter[0], radius_parameter[1],max_min_v[0], max_min_v[1])
        self.save_raster(iuh_2yr[0], Names.iuhAverage2yrRasName)
        self.save_raster(iuh_2yr[1], Names.iuhStandardDeviation2yrRasName)

        #10yr
        logger.info("10 yr ...")
        radius_parameter = self.parameter.parameter_database.iuh_10yr
        iuh_10yr = iuh.generate_travel_time_average_standard_deviation(radius_parameter[0], radius_parameter[1],max_min_v[0], max_min_v[1])
        self.save_raster(iuh_10yr[0], Names.iuhAverage10yrRasName)
        self.save_raster(iuh_10yr[1], Names.iuhStandardDeviation10yrRasName)

        #100yr
        logger.info("100 yr ...")
        radius_parameter = self.parameter.parameter_database.iuh_100yr
        iuh_100yr = iuh.generate_travel_time_average_standard_deviation(radius_parameter[0], radius_parameter[1],max_min_v[0], max_min_v[1])
        self.save_raster(iuh_100yr[0], Names.iuhAverage100yrRasName)
        self.save_raster(iuh_100yr[1], Names.iuhStandardDeviation100yrRasName)

    @property
    def iuh_t0_2yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhAverage2yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhAverage2yrRasName)

        return raster
    
    @property
    def iuh_delta_2yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhStandardDeviation2yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhStandardDeviation2yrRasName)

        return raster
    
    @property
    def iuh_t0_10yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhAverage10yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhAverage10yrRasName)

        return raster
    
    @property
    def iuh_delta_10yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhStandardDeviation10yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhStandardDeviation10yrRasName)

        return raster
    
    @property
    def iuh_t0_100yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhAverage100yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhAverage100yrRasName)

        return raster
    
    @property
    def iuh_delta_100yr_raster(self)->Raster:
        raster = self.get_raster(Names.iuhStandardDeviation100yrRasName)

        if raster is None:
            self.__create_iuh_rasters()
            raster = self.get_raster(Names.iuhStandardDeviation100yrRasName)

        return raster


#endregion

#region subarea

    @property
    def subarea_raster(self)->Raster:
        raster = self.get_raster(Names.subareaRasName)

        if raster is None:
            if self.field_raster is not None:
                logging.info("Creating subarea raster and vector ...")
                raster, raster1_max = RasterExtension.get_overlay_raster(self.field_raster, self.subbasin_raster)
                
                #re-order the id and return the old id to new id dict
                old_id_to_new_id_dict = Delineation.reorder_raster_id(raster)
                raster = self.save_raster(raster, Names.subareaRasName, True, True)

                #convert to vector and assign field and subbasin id
                vector = RasterExtension.raster_to_vector(raster)
                vector = VectorExtension.decompsite_overlay_id(vector, old_id_to_new_id_dict, "FieldId", "SubbasinId", raster1_max)
                self.save_vector(vector, Names.subareaShpName, True, True)
        return raster


    @property
    def subarea_vector(self)->Raster:
        vector = self.get_vector(Names.subareaShpName)

        if vector is None:
            raster = self.subarea_raster
            vector = self.get_vector(Names.subareaShpName)

        return vector
    
    @property
    def subarea_cellindex_df(self)->pd.DataFrame:
        """The CellSubarea"""       

        nodata = self.mask_refined_with_subbasin_raster.configs.nodata
        cell_index = 0
        cell_subarea = {}
        for row in range(self.inputs.rows):
            for col in range(self.inputs.columns):
                if self.mask_refined_with_subbasin_raster[row, col] == nodata:
                    continue
                cell_subarea[cell_index] = self.subarea_raster[row, col]
                cell_index = cell_index + 1

        df = pd.DataFrame.from_dict(cell_subarea, orient="index")
        df.reset_index(inplace=True)
        df.columns = ['CellIndex','SubareaId']

        return df
    
    @property
    def subarea_df(self)->pd.DataFrame:
        """
        Return subarea as dataframe
        """
        logger.info("Creating subarea ...")
        fieldIds = VectorExtension.get_unique_field_value(self.subarea_vector, "FieldId")
        field_df = pd.DataFrame.from_dict(fieldIds, orient="index")
        field_df.columns = ["FieldId"]

        subbasinIds = VectorExtension.get_unique_field_value(self.subarea_vector, "SubbasinId")
        subbasin_df = pd.DataFrame.from_dict(subbasinIds, orient="index")
        subbasin_df.columns = ["SubbasinId"]

        area_df = RasterExtension.get_category_area_ha_dataframe(self.subarea_raster, "Area")

        elevation_df = RasterExtension.get_zonal_statistics(self.dem_clipped_raster_for_model, self.subarea_raster, "mean","Elevation")
        slope_df = RasterExtension.get_zonal_statistics(self.slope_percent_raster, self.subarea_raster, "mean","Slope")
        uslep_df = RasterExtension.get_zonal_statistics(self.uslep_raster, self.subarea_raster, "mean","USLE_P")
        moist_init_df = RasterExtension.get_zonal_statistics(self.initial_soil_moisture_raster, self.subarea_raster, "mean","MoistureInitial")
        flow_acc_df = RasterExtension.get_zonal_statistics(self.flow_acc_raster, self.subarea_raster, "mean","FlowAccumulationAverage")

        wetland_flag_raster = self.wetland_raster.con(f"value == {self.wetland_raster.configs.nodata}", 0, 1)
        wetland_area_ha_df = RasterExtension.get_zonal_statistics(wetland_flag_raster, self.subarea_raster, "total","wetland_count") * self.inputs.cellsize_ha
        wetland_area_ha_df.fillna(0,inplace=True)
        wetland_area_ha_df.columns = ["wetland_area_ha"]
        
        #iuh
        iuh_t0_2yr_df = RasterExtension.get_zonal_statistics(self.iuh_t0_2yr_raster, self.subarea_raster, "mean","TravelTimeAverage2")
        iuh_t0_10yr_df = RasterExtension.get_zonal_statistics(self.iuh_t0_10yr_raster, self.subarea_raster, "mean","TravelTimeAverage10")
        iuh_t0_100yr_df = RasterExtension.get_zonal_statistics(self.iuh_t0_100yr_raster, self.subarea_raster, "mean","TravelTimeAverage100")

        iuh_delta_2yr_df = RasterExtension.get_zonal_statistics(self.iuh_delta_2yr_raster, self.subarea_raster, "mean","TravelTimeStd2")
        iuh_delta_10yr_df = RasterExtension.get_zonal_statistics(self.iuh_delta_10yr_raster, self.subarea_raster, "mean","TravelTimeStd10")
        iuh_delta_100yr_df = RasterExtension.get_zonal_statistics(self.iuh_delta_100yr_raster, self.subarea_raster, "mean","TravelTimeStd100")

        #merge
        subarea_df = pd.concat([field_df, subbasin_df, area_df, elevation_df, slope_df, uslep_df, moist_init_df, flow_acc_df, wetland_area_ha_df, 
                   iuh_t0_2yr_df,iuh_t0_10yr_df,iuh_t0_100yr_df, iuh_delta_2yr_df,iuh_delta_10yr_df,iuh_delta_100yr_df], axis=1)
        
        #calculate wetland fraction
        subarea_df["WetlandFraction"] = subarea_df["wetland_area_ha"] / subarea_df["Area"]
        subarea_df["WetlandFraction"] = subarea_df["WetlandFraction"].fillna(0).infer_objects(copy=False)

        #1 for topography weight
        subarea_df["TopographyWeight"] = 1

        #1/10 of subarea area
        subarea_df["LateralWidth"] = np.sqrt(subarea_df["Area"] * 10000) / 10

        #
        subarea_df.index.name = "Id"
        subarea_df.reset_index(inplace=True)

        return subarea_df[["Id","SubbasinId","FieldId","Area","Elevation","Slope","USLE_P","MoistureInitial","FlowAccumulationAverage","WetlandFraction",
                            "TravelTimeAverage2","TravelTimeAverage10","TravelTimeAverage100",
                            "TravelTimeStd2","TravelTimeStd10","TravelTimeStd100",
                            "TopographyWeight","LateralWidth"]]

#endregion

    @property
    def offsite_watering_raster(self)->Raster:
        raster = self.get_raster(Names.offsiteWinteringRasName)
        if raster is None:
            if self.inputs.offsite_watering_vector is not None:
                raster = VectorExtension.vector_to_raster(self.inputs.offsite_watering_vector, self.dem_clipped_raster_for_model)
                self.save_raster(raster, Names.offsiteWinteringRasName)
        return raster

    def delineate_watershed(self):
        """watershed delineation which basically delineate stream and subbasins"""
        subbasin = self.subbasin_vector
        dem_for_model = self.dem_clipped_raster_for_model
        reach = self.reach_vector
        soil_moisture = self.initial_soil_moisture_raster
        slope_percent = self.slope_percent_raster
        wetland = self.wetland_raster
        usle_p = self.uslep_raster
        offsite_watering = self.offsite_watering_raster
        tile_drain = self.tile_drain_raster
        wascobs = self.wascob_drainage_area_raster
