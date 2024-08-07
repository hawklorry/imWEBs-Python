import os
from whitebox_workflows import Raster, Vector
from .parameters import parameters
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

import logging
logger = logging.getLogger(__name__)
        
class Outputs(FolderBase):
    """
    Output folder where all intermediate and final processed files are saved
    """
    def __init__(self, output_folder:str, input_folder:str, database_folder:str,
                 stream_threshold_area_ha:float = 10,
                 wetland_min_area_ha:float = 0.1,
                 wetland_riparian_contribution_area_ha:float = 300,
                 wetland_stream_buffer_distance_m: float = 0) -> None:
        super().__init__(output_folder)

        self.stream_threshold_area_ha = stream_threshold_area_ha
        self.wetland_min_area_ha = wetland_min_area_ha
        self.wetland_riparian_contribution_area_ha = wetland_riparian_contribution_area_ha
        self.wetland_stream_buffer_distance_m = wetland_stream_buffer_distance_m

        self.inputs = Inputs(input_folder)
        self.parameter = parameters(database_folder)
        
        self.structures = {}
        for type in Structure.structure_types:
            boundary_vector = getattr(self.inputs, f"{type}_boundary_vector")
            if boundary_vector is not None:
                self.structures[type] = Structure(
                    structure_type=type,
                    output_folder=self.folder,
                    dem_raster=self.dem_clipped_burned_filled_raster,
                    structure_polygon_vector = boundary_vector, 
                    structure_outlet_point_vector = getattr(self.inputs, f"{type}_outlet_vector"),
                    structure_area_threshold_ha = self.wetland_min_area_ha if type == "wetland" else 0, 
                    structure_split_max_num = 3 if type == "wetland" else 1)

#region DEM processing

    @property
    def mask_raster(self):
        raster = self.get_raster(Names.maskRasName)
 
        if raster is None:
            #try user provided boundary shapefile
            if self.inputs.boundary_vector is not None:
                logger.debug(f"Creating mask using user-defined boundary shapefile ... ")
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.boundary_vector, base_raster = self.inputs.dem_raster)
                raster = raster.con(f"value = {raster.configs.nodata}", self.inputs.nodata, 1)                
            #try use soil and landuse 
            elif self.inputs.soil_raster is not None and self.inputs.landuse_raster is not None:
                logger.debug(f"Creating mask using user-defined boundary shapefile ... ")
                raster = self.inputs.create_new_raster()
                raster = self.inputs.dem_raster.con(f"value = {self.inputs.nodata}", self.inputs.nodata, 1)
                raster = self.inputs.soil_raster.con(f"value = {self.inputs.soil_raster.configs.nodata}", self.inputs.nodata, raster)
                raster = self.inputs.landuse_raster.con(f"value = {self.inputs.landuse_raster.configs.nodata}", self.inputs.nodata, raster)

            if raster is not None:
                self.save_raster(raster, Names.maskRasName)

        return raster
    
    @property
    def mask_refined_with_subbasin_raster(self):
        raster = self.get_raster(Names.maskRefindedWithSubbasinRasName)

        if raster is None:
            raster = self.subbasin_raster.con(f"value = {self.inputs.nodata}", self.inputs.nodata, 1)
            raster = self.inputs.soil_raster.con(f"value = {self.inputs.soil_raster.configs.nodata}", self.inputs.nodata, raster)
            raster = self.inputs.landuse_raster.con(f"value = {self.inputs.landuse_raster.configs.nodata}", self.inputs.nodata, raster)

            self.save_raster(raster, Names.maskRefindedWithSubbasinRasName)

        return

    @property 
    def dem_clipped_raster(self):
        """
        Clipped DEM by mask
        """
        raster = self.get_raster(Names.demClippedName)

        if raster is None:
            raster = self.mask_raster.con("value = 1", self.inputs.dem_raster, self.inputs.nodata)
            self.save_raster(raster, Names.demClippedName)

        return raster

    @property 
    def dem_clipped_burned_raster(self):
        """
        Burned DEM with user-provided stream shapefile
        """
        raster = self.get_raster(Names.demBurnedName)

        if raster is None:
            raster = self.wbe.fill_burn(dem = self.dem_clipped_raster, streams = self.inputs.stream_network_user_vector)
            self.save_raster(raster, Names.demBurnedName)

        return raster
    
    @property
    def dem_clipped_burned_filled_raster(self):
        """
        Filled DEM
        """
        raster = self.get_raster(Names.demFilledName)

        if raster is None:
            raster = self.wbe.fill_depressions(self.dem_clipped_burned_raster)
            self.save_raster(raster, Names.demFilledName)

        return raster

#endregion
    
#region farm & field

    def __remove_non_agriculture_cell(self, raster:Raster)->Raster:
        """
        remove non agriculture cells

        Replace filterAgriLanduse
        """
        raster_with_only_algriculture = raster.farm_raster.deep_copy()
        algricultrual_landuses = self.parameter.bmp_database.algricultural_landuses

        for row in raster.configs.rows:
            for col in raster.configs.columns:
                landuse = self.mapped_landuse_raster[row, col]
                
                if landuse > 0 and landuse not in algricultrual_landuses:
                    raster_with_only_algriculture[row, col] = raster.configs.nodata

        return raster_with_only_algriculture

    @property
    def farm_raster(self)->Raster:
        raster = self.get_raster(Names.farmRasName)
    
        if raster is None:
            if self.inputs.farm_vector is not None:
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.farm_vector, base_raster = self.inputs.dem_raster)
                self.save_raster(raster, Names.farmRasName)

        return raster
    
    @property
    def farm_without_agriculture_raster(self)->Raster:
        raster = self.get_raster(Names.farmWithOnlyAgricultureRasName)

        if raster is None:
            raster = self.__remove_non_agriculture_cell(self.farm_raster)
            raster = self.mask_raster.con("value = 1", raster, raster.configs.nodata)
            self.save_raster(raster, Names.farmWithOnlyAgricultureRasName)

        return raster

    
    @property
    def field_raster(self)->Raster:
        raster = self.get_raster(Names.fieldRasName)
    
        if raster is None:
            if self.inputs.field_vector is not None:
                raster = self.wbe.vector_polygons_to_raster(input = self.inputs.field_vector, base_raster = self.inputs.dem_raster)
                self.save_raster(raster, Names.farmRasName)

        return raster
    
    @property
    def field_without_agriculture_raster(self)->Raster:
        raster = self.get_raster(Names.fieldWithOnlyAgricultureRasName)

        if raster is None:
            raster = self.__remove_non_agriculture_cell(self.field_raster)
            raster = self.mask_raster.con("value = 1", raster, raster.configs.nodata)
            self.save_raster(raster, Names.fieldWithOnlyAgricultureRasName)

        return raster

#endregion    

#region parameters

    @property
    def mapped_soil_raster(self)->Raster:
        """
        mapped soil raster based on lookup table
        """
        raster = self.get_raster(Names.soilMappedName)

        if raster is None:
            raster = self.inputs.lookup_soil.mapped_raster
            self.save_raster(raster, Names.soilMappedName)

        return raster
    
    @property
    def mapped_landuse_raster(self)->Raster:
        """
        mapped landuse raster based on lookup table
        """
        raster = self.get_raster(Names.landuseMappedName)

        if raster is None:
            raster = self.inputs.lookup_landuse.mapped_raster
            self.save_raster(raster, Names.landuseMappedName)

        return raster

    @property
    def uslep_raster(self)->Raster:
        """
        use default usle P as 1, just copy from the mask
        """
        raster = self.get_raster(Names.uslePName)
        if raster is None:
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
            self.save_raster(raster, Names.fieldCapName)       

        return raster
    
    @property
    def manning_raster(self)->Raster:
        """
        manning from landuse and landuse parameter table in parameter database
        """
        raster = self.get_raster(Names.manningName)
        if raster is None:
            raster = RasterExtension.reclassify(self.mapped_landuse_raster, self.parameter.get_parameter_lookup("MANNING","landuse"), self.subbasin_raster)
            self.save_raster(raster, Names.manningName)

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
            self.save_raster(raster, Names.velocityName)
        return raster
           
    @property
    def wetness_index_raster(self)->Raster:
        """
        wetness index
        """
        raster = self.get_raster(Names.wetnessIndexName)

        if raster is None:
            raster = (self.flow_acc_raster * self.inputs.cellsize_m2).log() / self.slope_radius_raster.tan()
            raster = self.subbasin_raster.con("value > 0", raster, raster.configs.nodata)
            self.save_raster(raster, Names.wetnessIndexName)
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

            wti = self.wetness_index_raster.max(maxWetnessIndex)
            ratio = (wti - minWetnessIndex) * (maxSaturation - minSaturation) / (maxWetnessIndex - minWetnessIndex) + minSaturation
            raster = ratio * self.field_capacity_raster
            raster = self.subbasin_raster.con("value > 0", raster, raster.configs.nodata)

            self.save_raster(raster, Names.moistureInitialName)
        return raster
    
    @property
    def potential_ruoff_coefficient_raster(self)->Raster:
        """
        potential runoff coefficient
        """

        raster = self.get_raster(Names.PRCName)

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

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    raster[row,col] = self.parameter.get_potential_runoff_coefficient(landuse, soil, slope, reachWaterSurfaceFraction)
           
            self.save_raster(raster, Names.PRCName)

        return raster
    
    @property
    def potential_ruoff_coefficient_accumulate_average_raster(self)->Raster:
        """
        accumulative potential runoff coefficient
        """

        raster = self.get_raster(Names.PRCAccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.potential_ruoff_coefficient_raster)

            self.save_raster(raster, Names.PRCAccAvgName)
        return raster
    
    @property
    def depression_storage_capacity_raster(self)->Raster:
        """
        depression storage
        """
        raster = self.get_raster(Names.DSCName)

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

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    raster[row,col] = self.parameter.get_depression_storage_capacity(landuse, soil, slope, reachWaterSurfaceFraction)
           
            self.save_raster(raster, Names.DSCName)

        return raster
    
    @property
    def depression_storage_capacity_accumulate_average_raster(self)->Raster:
        """
        depresion storage accumulative
        """

        raster = self.get_raster(Names.DSCAccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.depression_storage_capacity_raster)

            self.save_raster(raster, Names.DSCAccAvgName)
        return raster
    
    @property
    def cn2_raster(self)->Raster:
        """
        CN2 parameter
        """

        raster = self.get_raster(Names.cn2Name)

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

                    reachWaterSurfaceFraction = self.__calculate_reach_water_surface_fraction(reach, reach_width,flow_dir)
                    cn2 = self.parameter.get_cn2(landuse, soil)
                    if reachWaterSurfaceFraction > 0:  # stream
                        cn2 = reachWaterSurfaceFraction * 100.0 + (1 - reachWaterSurfaceFraction) * cn2
                        cn2 = max(cn2, 35.0)
                        cn2 = min(cn2, 100.0)

                    raster[row,col] = cn2
           
            self.save_raster(raster, Names.cn2Name)

        return raster
    
    @property
    def cn2_accumulate_average_raster(self)->Raster:
        raster = self.get_raster(Names.Cn2AccAvgName)

        if raster is None:
            raster = self.__value_accumulate_d8(self.cn2_raster)

            self.save_raster(raster, Names.Cn2AccAvgName)
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
    def flow_direction_raster(self)->Raster:
        flow_dir_raster = self.get_raster(Names.flowDirD8FinalName)     

        if flow_dir_raster is None:
            if len(self.structures) > 0:                
                #if there are some structure, use the structure to get the flow direction
                #merge all structure boundary and outlets to get the final flow direction.
                structure_boundary_rasters = []
                structure_outlet_rasters = []
                for type,struc in self.structures.items():
                    structure_outlet_rasters.append(struc.outlet_raster)
                    structure_boundary_rasters.append(struc.boundary_raster)    
                combined_structure_boundary_raster = RasterExtension.combine_structure_rasters(rasters=structure_boundary_rasters, shape_type="polygon")
                combined_structure_outlet_raster = RasterExtension.combine_structure_rasters(rasters=structure_outlet_rasters, shape_type="point")
                
                #get flow direction considering the impact of structures
                flow_dir_raster = Structure.get_flow_direction(
                    combined_structure_boundary_raster, 
                    combined_structure_outlet_raster, 
                    self.dem_clipped_burned_filled_raster)
            else:
                #if there are no structure, use the dem directly
                flow_dir_raster = self.wbe.d8_pointer(dem = self.dem_clipped_burned_filled_raster)
            self.save_raster(flow_dir_raster, Names.flowDirD8FinalName)
        
        return flow_dir_raster

    @property
    def flow_acc_raster(self)->Raster:
        raster = self.get_raster(Names.flowAccName)

        if raster is None:  
            raster = self.wbe.d8_flow_accum(raster = self.flow_direction_raster, input_is_pointer = True)
            self.save_raster(raster, Names.flowAccName)

        return raster
    
    @property
    def flow_length_raster(self)->Raster:        
        raster = self.get_raster(Names.flowLengthName)

        if raster is None:
            raster = Delineation.get_flow_path_length(flow_dir_raster=self.flow_direction_raster)
            self.save_raster(raster, Names.flowLengthName)

        return raster    

    @property
    def stream_network_raster(self)->Raster:
        raster = self.get_raster(Names.streamNetworkRasName)
   
        if raster is None:       
            #get streams from the flow accumuation     
            raster = self.wbe.extract_streams(flow_accumulation = self.flow_acc_raster, threshold = self.stream_threshold_area_ha / self.inputs.cellsize_ha)
            
            #fix it as some of the structure streams may be below the threshold            
            raster = Delineation.build_stream_network_link_to_outlets(raster, self.flow_direction_raster,self.stream_outlets_raster)

            #save it
            self.save_raster(raster, Names.streamNetworkRasName)

        return raster    
    
    @property
    def stream_network_vector(self)->Vector:
        vector = self.get_vector(Names.streamNetworkShpName)
   
        if vector is None:            
            vector = self.wbe.raster_streams_to_vector(streams = self.stream_network_raster, d8_pointer = self.flow_direction_raster)
            self.save_vector(vector, Names.streamNetworkRasName)

        return vector    
    
    @property
    def stream_outlets_raster(self)->Raster:
        """
        the raster of all stream outlets
        """
        raster = self.get_raster(Names.streamOutletsRasName)

        if raster is None:
            raster = self.wbe.raster_to_vector_points(self.stream_outlets_vector)
            self.save_raster(raster, Names.streamOutletsRasName)

        return raster

    @property
    def stream_outlets_vector(self)->Vector:
        """
        the stream outlets considering structures, user-defined outlets and reservoirs
        """
        vector = self.get_vector(Names.streamOutletsShpName)

        if vector is None:
            #merge the pour points and user-provided reservoir and outlets
            outlet_vectors = []

            #add the pour point
            pour_points_vector = Delineation.get_pour_points(
                self.stream_network_raster, 
                self.flow_direction_raster, 
                [structure.boundary_raster for structure in self.structures])
            outlet_vectors.append(pour_points_vector)
            
            #add user-defined outlets
            if self.inputs.outlet_vector is not None:
                outlet_vectors.append(self.wbe.jenson_snap_pour_points(pour_pts = self.inputs.outlet_vector,streams = self.stream_network_raster))

            #add reservoir points
            if self.inputs.reservoir_vector is not None:
                outlet_vectors.append(self.wbe.jenson_snap_pour_points(pour_pts = self.inputs.reservoir_vector,streams = self.stream_network_raster))

            #add structure outlets
            if len(self.structures) > 0:
                outlet_vectors.append([structure.outlet_vector for structure in self.structures])

            vector = self.wbe.merge_vectors(outlet_vectors)
            self.save_vector(vector, Names.streamOutletsShpName)

        return vector

    @property
    def subbasin_raster(self)->Raster:
        raster = self.get_raster(Names.subbasinRasName)

        if raster is None:
            #get subbasins
            raster = self.wbe.watershed(d8_pointer=self.flow_direction_raster, pour_points=self.stream_outlets_vector)

            #fix the subbasins considering the structures
            for type,structure in self.structures:
                structure.repair_subbasin(raster)
            
            #reorder the subbasin starting from 1
            Delineation.reorder_raster_id(raster)

            #reorder the structure
            for type,structure in self.structures:
                structure.reorder_after_subbasin(raster)

            #save the subbasin raster
            self.save_raster(raster, Names.subbasinRasName)

        return raster
    
    @property
    def slope_radius_raster(self)->Raster:
        raster = self.get_raster(Names.slopeRadiusName)

        if raster is None:
            raster = (self.slope_degree_raster * math.pi / 180).tan()
            self.save_raster(Names.slopeRadiusName)

        return raster
    
    @property
    def slope_degree_raster(self)->Raster:        
        raster = self.get_raster(Names.slopeDegName)

        if raster is None:
            raster = self.wbe.slope(dem = self.dem_clipped_burned_filled_raster)
            self.save_raster(Names.slopeDegName)

        return raster

    @property
    def stream_order_raster(self)->Raster:
        raster = self.get_raster(Names.streamOrderName)  

        if raster is None:
            rater = self.wbe.strahler_stream_order(d8_pntr = self.flow_direction_raster, streams_raster = self.stream_network_raster)
            self.save_raster(raster, Names.streamOrderName)

        return raster
            

#endregion

#region reach

    @property
    def reach_raster(self)->Raster:
        raster = self.get_raster(Names.reachRasName) 

        if raster is None:
            raster = self.stream_network_raster.con("value >= 0", self.subbasin_raster, self.subbasin_raster.configs.nodata)
            self.save_raster(raster, Names.reachRasName)

        return raster

    # def raster_streams_to_vector_imwebs(self):
    #     """
    #     replace RasterStreamsToVectorIMWEBs
    #     """
    #     row, col, x, y = 0, 0, 0, 0
    #     LnOf2 = 0.693147180559945
    #     dX = [1, 1, 1, 0, -1, -1, -1, 0]
    #     dY = [-1, 0, 1, 1, 1, 0, -1, -1]
    #     inflowing_vals = [16, 32, 64, 128, 1, 2, 4, 8]

    #     try:
    #         streams = WhiteboxRaster(streams_header, "r")
    #         rows = streams.get_number_rows()
    #         cols = streams.get_number_columns()
    #         no_data = streams.get_no_data_value()
    #         grid_res_x = streams.get_cell_size_x()
    #         grid_res_y = streams.get_cell_size_y()
    #         diag_grid_res = math.sqrt(grid_res_x * grid_res_x + grid_res_y * grid_res_y)
    #         grid_lengths = [diag_grid_res, grid_res_x, diag_grid_res, grid_res_y, diag_grid_res, grid_res_x, diag_grid_res, grid_res_y]
    #         east = streams.get_east() - grid_res_x / 2.0
    #         west = streams.get_west() + grid_res_x / 2.0
    #         EW_range = east - west
    #         north = streams.get_north() - grid_res_y / 2.0
    #         south = streams.get_south() + grid_res_y / 2.0
    #         NS_range = north - south

    #         pntr = WhiteboxRaster(pointer_header, "r")

    #         fields = [DBFField() for _ in range(1)]
    #         fields[0].set_name("VALUE")
    #         fields[0].set_data_type(DBFField.DBFDataType.NUMERIC)
    #         fields[0].set_field_length(10)
    #         fields[0].set_decimal_count(3)

    #         output = ShapeFile(output_file_name, ShapeType.POLYLINE, fields)

    #         FID = 0
    #         stream_parts = defaultdict(list)
    #         stream_points = defaultdict(PointsList)

    #         for row in range(rows):
    #             for col in range(cols):
    #                 stream_value = streams.get_value(row, col)
    #                 if stream_value > 0:
    #                     num_neighbouring_stream_cells = 0
    #                     is_upstream_different = False
    #                     for c in range(8):
    #                         x = col + dX[c]
    #                         y = row + dY[c]
    #                         if streams.get_value(y, x) > 0 and pntr.get_value(y, x) == inflowing_vals[c]:
    #                             num_neighbouring_stream_cells += 1
    #                             if streams.get_value(y, x) != stream_value:
    #                                 is_upstream_different = True
    #                     if num_neighbouring_stream_cells != 1 or is_upstream_different:
    #                         FID += 1
    #                         link_length = 0
    #                         points = PointsList()
    #                         if stream_value in stream_parts:
    #                             points = stream_points[stream_value]
    #                             stream_parts[stream_value].append(len(points))
    #                         else:
    #                             stream_parts[stream_value].append(0)
    #                             stream_points[stream_value] = points

    #                         x = col
    #                         y = row
    #                         previous_flow_dir = -99
    #                         flag = True
    #                         while flag:
    #                             flow_dir = pntr.get_value(y, x)
    #                             if flow_dir > 0:
    #                                 if flow_dir != previous_flow_dir:
    #                                     x_coord = west + (x / cols) * EW_range
    #                                     y_coord = north - (y / rows) * NS_range
    #                                     points.add_point(x_coord, y_coord)
    #                                     previous_flow_dir = flow_dir

    #                                 c = int(math.log(flow_dir) / LnOf2)
    #                                 if c > 7:
    #                                     return

    #                                 x += dX[c]
    #                                 y += dY[c]
    #                                 link_length += grid_lengths[c]

    #                                 if streams.get_value(y, x) <= 0 or streams.get_value(y, x) != stream_value:
    #                                     flag = False
    #                                 else:
    #                                     num_neighbouring_stream_cells = 0
    #                                     for d in range(8):
    #                                         x2 = x + dX[d]
    #                                         y2 = y + dY[d]
    #                                         if streams.get_value(y2, x2) > 0 and pntr.get_value(y2, x2) == inflowing_vals[d]:
    #                                             num_neighbouring_stream_cells += 1
    #                                     if num_neighbouring_stream_cells > 1:
    #                                         flag = False
    #                             else:
    #                                 flag = False

    #                             if not flag:
    #                                 x_coord = west + (x / cols) * EW_range
    #                                 y_coord = north - (y / rows) * NS_range
    #                                 points.add_point(x_coord, y_coord)

    #         for stream_id in stream_parts.keys():
    #             parts = stream_parts[stream_id]
    #             array = [parts[i] for i in range(len(parts))]
    #             line = PolyLine(array, stream_points[stream_id].get_points_array())
    #             row_data = [stream_id]
    #             output.add_record(line, row_data)

    #         output.write()

    #         pntr.close()
    #         streams.close()

    #     except (OutOfMemoryError, Exception) as oe:
    #         Logger.getLogger(Watershed.class.get_name()).log(Level.SEVERE, None, oe)


    @property
    def reach_width_raster(self)->Raster:
        """
        calculate reach width for 2-year design storm, will use-defined parameter later
        """
        return self._get_reach_width_depth_raster(2, False)
    
    @property
    def reach_depth_raster(self)->Raster:
        """
        calculate reach depth for 2-year design storm, will use-defined parameter later
        """
        return self._get_reach_width_depth_raster(2, True)
    
    def _get_reach_width_depth_raster(self, design_storm, isdepth:bool)->Raster:
        """
        calculate reach width/depth raster using given design storm
        """
        file_name = Names.reachWidthName
        if isdepth:
            file_name = Names.reachDepthName

        raster = self.get_raster(file_name)
        if raster is None:
            parameter = self.parameter.get_reach_width_parameter(design_storm)          
            if isdepth:
                parameter = self.parameter.get_reach_depth_parameter(design_storm) 
            raster = (self.flow_acc_raster * self.inputs.cellsize_m2 * parameter.A) ** parameter.B
            raster = self.stream_network_raster.con("value > 0", raster, raster.configs.nodata)
            self.save_raster(raster, file_name)

        return raster

#endregion

    def generate_bmp_database(self):
        self.parameter.bmp_database.populate_database(
            self.subbasin_raster, 
            self.inputs.field_raster, 
            self.inputs.farm_raster,
            self.flow_acc_raster,
            self.potential_ruoff_coefficient_raster,
            self.depression_storage_capacity_raster,
            self.cn2_raster)
    
    def generate_watershed_parameters(self):
        mask = self.mask_raster
        uslp = self.uslep_raster
        reach_depth = self.reach_depth_raster
        reach_width = self.reach_width_raster
        field_capacity = self.field_capacity_raster
        manning = self.manning_raster
        velocity = self.velocity_raster
        wetness_index = self.wetness_index_raster
        initial_soil_moisture = self.initial_soil_moisture_raster

        #build the reach parameter table
        #use the one from China
        #reach = Reach(self)
        #reach.build_reach_parameters()

        #generate all the bmp database
        self.generate_bmp_database()

        #build structure bmp parameter table
        #buildBMPParMgtTables
  
        # // Build livestock parameter table
        # DataTable livestockPar = imwebs.getParameterDS().getTable(ParameterDatasetStructure.DefaultLivestockParameterTableName);
        # livestockPar.setName(BMPDatasetStructure.LivestockParameterTableName);
        # imwebs.getProject().getBMPDS().replaceTable(livestockPar);

        # // Build manure_and_nutrient_parameter table
        # DataTable manureParTable = imwebs.getParameterDS().getTable(ParameterDatasetStructure.manureAndNutrientParameterTableName);
        # imwebs.getProject().getBMPDS().replaceTable(manureParTable);

        # // Build LS_parameter table
        # DataTable LSParTable = imwebs.getParameterDS().getTable(ParameterDatasetStructure.LSParameterTableName);
        # imwebs.getProject().getBMPDS().replaceTable(LSParTable);

        # // Build BMP index table
        # imwebs.getProject().getBMPDS().replaceTable(imwebs.buildBMPIndexTable());

        # // Build subbasin multiplier table
        # Tools.buildSubbasinMultiplierTable(imwebs.getProject().getBMPDS().getPath());

        # // Save BMP database
        # imwebs.getProject().getBMPDS().save();
        
        # // Ensure all rasters in \Watershed\Output have same NoDataValue        
        # Tools.VerifyAndFixAllRastersInFolder(imwebs.getWhiteboxToolsPath(), getWatershedOutputFolder());
    




