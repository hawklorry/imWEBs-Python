import math
from .database.parameter.parameter_database import ParameterDatabase
from .database.bmp.bmp_database import BMPDatabase, reach_width_depth_parameter
from .folder_base import FolderBase 
from .names import Names    

class Parameters(FolderBase):
    """all the parameters from parameter database and bmp database. It exposes necessary """
    GRASS_ID = 38

    def __init__(self, database_folder:str)->None:
        super().__init__(database_folder)

        self.parameter_database = ParameterDatabase(self.get_file_path(Names.parameterDatabaseName))
        self.bmp_database = BMPDatabase(self.get_file_path(Names.bmpDatabaseName))
        self.reach_width_parameters = {2: reach_width_depth_parameter(2, 1, 0.56),
                                       10: reach_width_depth_parameter(10, 1.2, 0.56),
                                       100: reach_width_depth_parameter(100, 1.4, 0.56)}
        
        self.reach_depth_parameters = {2: reach_width_depth_parameter(2, 0.04, 0.45),
                                       10: reach_width_depth_parameter(10, 0.12, 0.52),
                                       100: reach_width_depth_parameter(100, 0.18, 0.55)}

    def get_reach_width_parameter(self, design_storm)->reach_width_depth_parameter:
        if design_storm in self.reach_width_parameters:
            return self.reach_width_parameters[design_storm]
        
        return reach_width_depth_parameter(design_storm, 1, 0.56)
    
    def get_reach_depth_parameter(self, design_storm)->reach_width_depth_parameter:
        if design_storm in self.reach_depth_parameters:
            return self.reach_depth_parameters[design_storm]
        
        return reach_width_depth_parameter(design_storm, 0.04, 0.45)

    # def get_reach_parameter(self, reach_id, parameter_name):
    #     return self.bmp_database.get_reach_parameter(reach_id, parameter_name)

    def get_parameter_lookup(self,parameter_name,parameter_type):
        return self.parameter_database.get_parameter_lookup(parameter_name,parameter_type)

    def get_potential_runoff_coefficient(self, landuse, soil, slope, reach_fraction):
        impervious_ratio = self.parameter_database.get_impervious_ratio(landuse)
        grass_prc = self.parameter_database.get_potential_runoff_coefficient(self.GRASS_ID, soil)
        base_prc = self.parameter_database.get_potential_runoff_coefficient(landuse, soil)
        base_slope = self.parameter_database.get_slope(landuse, soil)

        return parameters.calculate_potential_runoff_coefficient(impervious_ratio, grass_prc, base_prc, base_slope, slope, reach_fraction)
    
    def get_depression_storage_capacity(self, landuse, soil, slope, reach_fraction):
        impervious_ratio = self.parameter_database.get_impervious_ratio(landuse)
        grass_dsc = self.parameter_database.get_depression_storage_capacity(self.GRASS_ID, soil)
        base_dsc = self.parameter_database.get_depression_storage_capacity(landuse, soil)
        base_slope = self.parameter_database.get_slope(landuse, soil)

        return parameters.calculate_depression_storage_capacity(impervious_ratio, grass_dsc, base_dsc, base_slope, slope, reach_fraction)

    def get_cn2(self, landuse, soil)->float:
        return self.parameter_database.get_cn2(landuse, soil)

    @staticmethod
    def calculate_potential_runoff_coefficient(impervious_ratio, grass_prc, base_prc, base_slope, slope, reach_fraction):
        slope_factor = (slope + base_slope) / (slope + base_slope) if (slope + base_slope) > 0 else 0
        impervious_part = base_prc + (1 - base_prc) * slope_factor
        prc = impervious_part
        
        if 0 < impervious_ratio < 1:  # urban
            pervious_part = grass_prc + (1 - grass_prc) * slope_factor
            prc = impervious_part * impervious_ratio + pervious_part * (1 - impervious_ratio)
        
        if reach_fraction > 0:  # stream
            prc = reach_fraction + (1 - reach_fraction) * prc
        
        prc = max(prc, 0.0)
        prc = min(prc, 1.0)
        
        return prc

    @staticmethod
    def calculate_depression_storage_capacity(impervious_ratio, grass_dsc, base_dsc, slope, reach_surface_fraction):
        slope_factor = math.exp(-9.5 * slope / 100.0)
        dsc = base_dsc * slope_factor
        
        if 0 < impervious_ratio < 1:  # urban
            dsc = (base_dsc * impervious_ratio + grass_dsc * (1 - impervious_ratio)) * slope_factor

        if reach_surface_fraction > 0:  # stream
            dsc = (1 - reach_surface_fraction) * dsc
            dsc = max(dsc, 0.0)
            dsc = min(dsc, 1.0)

        return dsc
