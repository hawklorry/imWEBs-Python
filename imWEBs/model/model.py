import os
from ..outputs import Outputs
from ..database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from ..names import Names
from .parameter_h5 import ParameterH5
from ..database.bmp.bmp_database import BMPDatabase

class Model:
    """
    Have the model here so all model related structures will be in one place
    """
    def __init__(self, model_folder:str) -> None:
        self.model_folder = model_folder
        self.model_input_folder = os.path.join(self.model_folder, "watershed", "input")
        self.model_output_folder = os.path.join(self.model_folder, "watershed", "output")
        self.model_database_folder = os.path.join(self.model_folder, "database")
        self.__outputs = None
        self.__bmp_database = None
        self.__hydroclimate = None
        self.__parameter_h5 = None

    def create_model_folder(self):
        if not os.path.exists(self.model_input_folder):
            os.makedirs(self.model_input_folder)
        if not os.path.exists(self.model_output_folder):
            os.makedirs(self.model_output_folder)
        if not os.path.exists(self.model_database_folder):
            os.makedirs(self.model_database_folder)

    @property
    def outputs(self)->Outputs:
        if self.__outputs is None:
            self.__outputs = Outputs(self.model_output_folder, self.model_input_folder, self.model_database_folder)
        return self.__outputs
    
    @property
    def bmp_databaes(self)->BMPDatabase:
        if self.__bmp_database is None:
            self.__bmp_database = BMPDatabase(os.path.join(self.model_database_folder,Names.bmpDatabaseName))
        return self.__bmp_database
    
    @property
    def hydroclimate(self)->HydroClimateDatabase:
        if self.__hydroclimate is None:
            self.__hydroclimate = HydroClimateDatabase(os.path.join(self.model_database_folder,Names.hydroclimateDatabasename))
        return self.__hydroclimate
    
    @property
    def parameter_h5(self)->ParameterH5:
        if self.__parameter_h5 is None:
            self.__parameter_h5 = ParameterH5(os.path.join(self.model_output_folder, Names.parameteH5Name))
        return self.__parameter_h5

    def delineate_watershed(self,
                            stream_threshold_area_ha:float = 10,   #stream thrshold area
                            wetland_min_area_ha:float = 0.1,       #min wetland area
                            design_storm_return_period = 2,        #design storm return period for reach width and depth
                            marginal_crop_land_simulation = False,
                            marginal_crop_land_non_agriculture_landuse_ids = None,
                            marginal_crop_land_buffer_size_m = 100,
                            marginal_crop_land_slope_threshold_percentage = 7,
                            marginal_crop_land_grass_type = 36):
        """watershed delineation""" 
        self.outputs.delineate_watershed(stream_threshold_area_ha, 
                                         wetland_min_area_ha, 
                                         design_storm_return_period, 
                                         marginal_crop_land_simulation, 
                                         marginal_crop_land_non_agriculture_landuse_ids, 
                                         marginal_crop_land_buffer_size_m, 
                                         marginal_crop_land_slope_threshold_percentage,
                                         marginal_crop_land_grass_type)

    def generate_parameters(self, reservoir_flow_routing:str, reservoir_flow_data_folder:str):
        """generate parameters"""

        #bmp database
        self.bmp_databaes.create_database_structure()
        self.bmp_databaes.create_spatial_relationship_tables(self.outputs)
        self.bmp_databaes.create_bmp_tables(self.outputs,reservoir_flow_routing, reservoir_flow_data_folder)


    def update_crop_rotation(self,crop_inventory_folder:str, first_year:int, last_year:int, include_grazing:bool):
        """update crop rotation"""
        if include_grazing and self.outputs.inputs.offsite_watering_vector is None:
            raise ValueError("Grazing requires offsite watering shapefile. Please add an offiste watering shapefile or turn off grazing in crop rotation.")
        self.bmp_databaes.update_crop_rotation_AAFC_crop_inventory(crop_inventory_folder, first_year, last_year, self.outputs, include_grazing)

    def generate_subarea(self)->int:
        """generate subarea, subareasoil and subarealanduse"""
        return self.bmp_databaes.create_subarea(self.outputs)

    def run(self, scenario_id, scenario_name):
        pass

