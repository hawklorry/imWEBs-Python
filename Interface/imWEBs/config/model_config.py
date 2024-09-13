from configparser import ConfigParser
import os
from whitebox_workflows import WbEnvironment
from ..raster_extension import RasterExtension
from ..vector_extension import VectorExtension
from ..names import Names
from ..outputs import Outputs
import shutil
import logging
from .config import Config

logger = logging.getLogger(__name__)

class ModelConfig(Config):
    """
    Config for watershed delineation and model structure creation
    """

    #the sections that are files
    file_sections = ["watershed","lookup","database","reach_bmp","structure_bmp","non_structure_bmp"]

    def __init__(self, config_file:str = None):
        super().__init__(config_file)
        self.is_valid = False 
        self.input_folder = ""
        
        self.__load()

    def __load(self):
        """
        load the config file, validate and copy the input files
        """

        if self.config_file is not None and os.path.exists(self.config_file):
            rasters = {}
            vectors = {}
            databases = {}
            lookups = {}

            file_exist_valid = True
            wbe = WbEnvironment()
            
            logger.debug(f"Loading model configuration file {self.config_file} ...")
            cf = ConfigParser()
            cf.read(self.config_file)
            for section, variables in self.config_variables.items():
                for var in variables:
                    logger.debug(f"Reading Section: {section}, Variable: {var} ...")
                    if section == "delineation":
                        value = Config.get_option_value_exactly(cf, section, var, valtyp=float)
                        setattr(self, var, value)
                        continue
                    else:
                        value = Config.get_option_value(cf, section, var)
                        setattr(self, var, value)

                    if value is None or len(value) <= 0:
                        continue

                    #check input folder
                    if var == "input_folder":
                        if os.path.exists(value):
                            self.input_folder = value
                        else:
                            file_exist_valid = False
                            raise ValueError(f"{var} = {value} doesn't exist!")
                    
                    #create model folder
                    if var == "model_folder":
                        self.model_folder = value
                        if not os.path.exists(value):
                            os.makedirs(value)
                        continue

                    if section in ModelConfig.file_sections:
                        file_path = os.path.join(self.input_folder, value)
                        if os.path.exists(file_path):
                            if "raster" in var:
                                rasters[var] = wbe.read_raster(file_path)
                            if "shapefile" in var:
                                vectors[var] = wbe.read_vector(file_path)
                            if section == "database":
                                databases[var] = value
                            if section == "lookup":
                                lookups[var] = value
                        else:
                            file_exist_valid = False
                            logger.warning(f"{var} = {value} doesn't exist!")

            #check rasters and vectors
            raster_valid = RasterExtension.check_rasters(rasters)
            vector_valid = VectorExtension.check_vectors(vectors)
            self.is_valid = file_exist_valid and raster_valid and vector_valid

            #copy all the input files to the model folder with standard name
            if self.is_valid:
                self.__create_model_folder()

                logger.debug(f"Copying input files to {self.input_folder} ...")
                for option, raster in rasters.items():
                    wbe.write_raster(raster, os.path.join(self.model_input_folder, Names.config_item_standard_name_lookup[option]))
                for option, vector in vectors.items():
                    VectorExtension.save_vector(vector, os.path.join(self.model_input_folder, Names.config_item_standard_name_lookup[option]))
                for option, databae_file in databases.items():
                    shutil.copyfile(os.path.join(self.input_folder, databae_file), os.path.join(self.model_database_folder, Names.config_item_standard_name_lookup[option]))
                for option, lookup_file in lookups.items():
                    shutil.copyfile(os.path.join(self.input_folder, lookup_file), os.path.join(self.model_input_folder, Names.config_item_standard_name_lookup[option]))

            #create model outputs object
            self.outputs = Outputs(self.model_output_folder, self.model_input_folder, self.model_database_folder)

    def __create_model_folder(self):
        """
        create model folder structure
        """
        self.model_input_folder = os.path.join(self.model_folder, "watershed", "input")
        self.model_output_folder = os.path.join(self.model_folder, "watershed", "output")
        self.model_database_folder = os.path.join(self.model_folder, "database")

        if not os.path.exists(self.model_input_folder):
            os.makedirs(self.model_input_folder)
        if not os.path.exists(self.model_output_folder):
            os.makedirs(self.model_output_folder)
        if not os.path.exists(self.model_database_folder):
            os.makedirs(self.model_database_folder)
    
    def delineate_watershed(self):
        """watershed delineation"""
        self.outputs.delineate_watershed()

    @property
    def config_variables(self)->str:
        return {
            "default":["input_folder"],

            #watershed definition
            "watershed":["dem_raster",
                         "soil_raster",
                         "landuse_raster",
                         "stream_shapefile",
                         "boundary_shapefile",
                         "farm_shapefile",
                         "field_shapefile",
                         "outlet_shapefile"
                        ],

            #lookup tables            
            "lookup":["soil_lookup","landuse_lookup"],

            #db3 databases
            "database":["hydroclimate"],

            #we only need the shapefile of bmps that will impact the watershed dilineation.
            #all existing and future ones should be included in the shapefile and could be
            #enabled or disabled in scenario design stage.
            #also assume that all shapefile has an ID column as the structure ids. This will be enforced. 
            "reach_bmp":[ "point_source_shapefile",
                          "flow_diversion_shapefile",
                          "reservoir_shapefile",
                          "wetland_boundary_shapefile","wetland_outlet_shapefile",
                          "manure_catch_basin_shapefile",
                          "grass_waterway_shapefile",
                          "access_management_shapefile",
                          "water_use_shapefile"
                          ],

            #wasco will be the outlet of the subbasin
            "structure_bmp":["dugout_boundary_shapefile",
                             "wascob_boundary_shapefile"],

            #feedlot will be delineated in a single subbasin, the catch basin will function as the outlet.
            "non_structure_bmp":["manure_feedlot_boundary_shapefile"],

            #delineation parameters
            "delineation":["stream_threshold_area_ha",
                        "wetland_min_area_ha",
                        "wetland_riparian_contribution_area_ha",
                        "wetland_stream_buffer_distance_m"],

            "marginal_crop_land":["non_agriculture_landuse_ids","buffer_size_m","slope_threshold_percentage"],
            "pasture_land":["non_agriculture_landuse_ids"],

            #model folder
            "model":["model_folder"]
        }