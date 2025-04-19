from configparser import ConfigParser
import os
from whitebox_workflows import WbEnvironment, Vector
from ..raster_extension import RasterExtension
from ..vector_extension import VectorExtension
from ..names import Names
import shutil
import logging
from .config import Config
from pathlib import Path
from ..model.model import Model

logger = logging.getLogger(__name__)

class ModelConfig(Config):
    """
    Config for watershed delineation and model structure creation
    """

    #the sections that are files
    file_sections = ["watershed","lookup","parameter","database","reach_bmp","structure_bmp","non_structure_bmp","manure_adjustment_bmp"]

    def __init__(self, config_file:str = None):
        super().__init__(config_file)
        self.input_folder = ""
        self.model = None
        
        self.__load()

    def __load(self):
        """
        load the config file, validate and copy the input files
        """

        if self.config_file is not None and os.path.exists(self.config_file):
            rasters = {}
            vectors = {}
            unique_id_vectors = {}
            databases = {}
            lookups = {}

            wbe = WbEnvironment()
            
            logger.info(f"Loading model configuration file {self.config_file} ...")
            cf = ConfigParser()
            cf.read(self.config_file)
            for section, variables in self.config_variables.items():
                for var in variables:
                    #logger.info(f"Reading Section: {section}, Variable: {var} ...")
                    if section == "delineation" and var != "use_all_pour_points_from_stream_threshold":
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
                            raise ValueError(f"{var} = {value} doesn't exist!")
                    
                    #create model folder
                    if var == "model_folder":
                        if not os.path.exists(value):
                            os.makedirs(value)
                        self.model = Model(value)
                        continue

                    if section in ModelConfig.file_sections or "shapefile" in var:
                        file_path = os.path.join(self.input_folder, value)
                        if os.path.exists(file_path):
                            if "raster" in var:
                                rasters[var] = wbe.read_raster(file_path)
                            if "shapefile" in var:
                                vectors[var] = wbe.read_vector(file_path)
                                if "bmp" in section:
                                    unique_id_vectors[var] = vectors[var]
                            if section == "database":
                                databases[var] = value
                            if section == "lookup" or section == "parameter":
                                lookups[var] = value
                        else:
                            raise ValueError(f"{var} = {value} doesn't exist!")
                    


            #check rasters and vectors
            RasterExtension.check_rasters(rasters)
            VectorExtension.check_vectors(unique_id_vectors)

            #copy all the input files to the model folder with standard name
            self.model.create_model_folder()
            logger.info(f"Copying input files to {self.input_folder} ...")

            logger.info("Rasters ...")
            for option, raster in rasters.items():
                logger.info(raster.file_name)
                wbe.write_raster(raster, os.path.join(self.model.model_input_folder, Names.config_item_standard_name_lookup[option]))
            
            logger.info("Vectors ...")
            for option, vector in vectors.items():
                logger.info(vector.file_name)
                VectorExtension.save_vector(vector, os.path.join(self.model.model_input_folder, Names.config_item_standard_name_lookup[option]))
            
            logger.info("Databases ...")
            for option, databae_file in databases.items():
                logger.info(databae_file)
                shutil.copyfile(os.path.join(self.input_folder, databae_file), os.path.join(self.model.model_database_folder, Names.config_item_standard_name_lookup[option]))
            
            logger.info("Lookup files ...")
            for option, lookup_file in lookups.items():
                logger.info(lookup_file)
                source_file = os.path.join(self.input_folder, lookup_file)
                target_file = os.path.join(self.model.model_input_folder, Names.config_item_standard_name_lookup[option])

                #we need to write the lookup file to utf8 so it could be loaded correctly in pandas later.
                Path(target_file).write_text(Path(source_file).read_text(), encoding="utf8") 

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
                         "outlet_shapefile" #not used right now
                        ],

            #lookup tables            
            "lookup":["soil_lookup",
                      "landuse_lookup"],

            #parameter
            "parameter":["SoilLookup"],

            #db3 databases
            "database":["hydroclimate"],

            #we only need the shapefile of bmps that will impact the watershed dilineation.
            #all existing and future ones should be included in the shapefile and could be
            #enabled or disabled in scenario design stage.
            #also assume that all shapefile has an ID column as the structure ids. This will be enforced. 
            "reach_bmp":[ "point_source_shapefile",
                          "flow_diversion_shapefile",
                          "reservoir_shapefile",
                          "wetland_boundary_shapefile",
                          "wetland_outlet_shapefile",
                          "manure_catch_basin_shapefile",
                          "grass_waterway_shapefile",
                          "access_management_shapefile",
                          "water_use_shapefile"
                          ],

            #wasco will be the outlet of the subbasin
            "structure_bmp":["dugout_boundary_shapefile",                             
                             "riparian_buffer_shapefile",
                             "filter_strip_shapefile",
                             "tile_drain_boundary_shapefile",
                             "tile_drain_outlet_shapefile",
                             "wascob_shapefile"],

            #feedlot will be delineated in a single subbasin, the catch basin will function as the outlet.
            "non_structure_bmp":["manure_feedlot_boundary_shapefile",
                                 "manure_feedlot_outlet_shapefile",
                                 "manure_storage_boundary_shapefile",
                                 "offsite_watering_shapefile"],

            "reservoir":["reservoir_flow_routing","reservoir_flow_data_folder"],

            #delineation parameters
            "delineation":["stream_threshold_area_ha",
                           "use_all_pour_points_from_stream_threshold",
                        "wetland_min_area_ha",
                        "wetland_riparian_contribution_area_ha",
                        "wetland_stream_buffer_distance_m"],

            "marginal_crop_land":[
                "marginal_crop_land_simulation",
                "marginal_crop_land_shapefile",
                "marginal_crop_land_non_agriculture_landuse_ids",
                "marginal_crop_land_buffer_size_m",
                "marginal_crop_land_slope_threshold_percentage",
                "marginal_crop_land_grass_type"],

            "pasture_crop_land":[
                "pasture_crop_land_simulation",
                "pasture_crop_land_shapefile",
                "pasture_crop_land_landuse_ids",
                "pasture_crop_land_grass_type"
            ],

            "manure_adjustment_bmp":[
                "manure_adjustment_incorporation_within_48h_shapefile",
                "manure_adjustment_application_setback_shapefile",
                "manure_adjustment_no_application_on_snow_shapefile",
                "manure_adjustment_spring_rather_than_fall_shapefile", 
                "manure_adjustment_based_on_n_limit_shapefile", 
                "manure_adjustment_based_on_p_limit_shapefile" 
            ],

            #crop rotation
            "crop_rotation":["method",
                              "AAFC_crop_inventory_folder",
                              "first_year",
                              "last_year",
                              "include_grazing"],

            #model folder
            "model":["model_folder"]
        }
    
#region delineation

    @property
    def use_all_pour_points_from_stream_threshold_property(self)->bool:
        value = self.get_config_value("use_all_pour_points_from_stream_threshold", False)
        
        if value is None:
            return False
        
        if isinstance(value, str) and (str(value).lower() == "yes" or str(value).lower() == "true"):
            return True
        
        return False

#endregion

#region marginal crop land

    @property
    def marginal_crop_land_simulation_property(self)->bool:
        value = self.get_config_value("marginal_crop_land_simulation", False)
        
        if value is None:
            return False
        
        if isinstance(value, str) and (str(value).lower() == "yes" or str(value).lower() == "true"):
            return True
        
        return False
    
    @property
    def marginal_crop_land_non_agriculture_landuse_ids_property(self):
        value = self.get_config_value("marginal_crop_land_non_agriculture_landuse_ids", optional = True)
         
        if isinstance(value, str) and len(value) > 0:
            return [int(id) for id in value.split(",")]
        
        return None
    
    @property 
    def marginal_crop_land_buffer_size_m_property(self)->int:
        return int(self.get_config_value("marginal_crop_land_buffer_size_m", 100))
    
    @property
    def marginal_crop_land_slope_threshold_percentage_property(self)->int:
        return int(self.get_config_value("marginal_crop_land_slope_threshold_percentage", 7))

    @property
    def marginal_crop_land_grass_type_property(self)->int:
        return int(self.get_config_value("marginal_crop_land_grass_type", 36))
    
#endregion

#region pasture crop land

    @property
    def pasture_crop_land_simulation_property(self)->bool:
        value = self.get_config_value("pasture_crop_land_simulation", False)
        
        if value is None:
            return False
        
        if isinstance(value, str) and (str(value).lower() == "yes" or str(value).lower() == "true"):
            return True
        
        return False
    
    @property
    def pasture_crop_land_landuse_ids_property(self):
        value = self.get_config_value("pasture_crop_land_landuse_ids", optional = True)
         
        if isinstance(value, str) and len(value) > 0:
            return [int(id) for id in value.split(",")]
        
        return None

    @property
    def pasture_crop_land_grass_type_property(self)->int:
        return int(self.get_config_value("pasture_crop_land_grass_type", 36))
    
#endregion

    def generate_pour_points_based_on_threshold_and_structures(self):
        self.model.generate_pour_points_based_on_threshold_and_structures(
            stream_threshold_area_ha = float(self.get_config_value("stream_threshold_area_ha", 10)),
            wetland_min_area_ha = float(self.get_config_value("wetland_min_area_ha", 0.1)))

    def delineate_watershed(self):
        """watershed delineation""" 
        self.model.delineate_watershed(
            stream_threshold_area_ha = float(self.get_config_value("stream_threshold_area_ha", 10)),
            use_all_pour_points_from_stream_threshold = self.use_all_pour_points_from_stream_threshold_property,
            wetland_min_area_ha = float(self.get_config_value("wetland_min_area_ha", 0.1)),
            design_storm_return_period = 2,
            marginal_crop_land_simulation = self.marginal_crop_land_simulation_property,
            marginal_crop_land_non_agriculture_landuse_ids = self.marginal_crop_land_non_agriculture_landuse_ids_property,
            marginal_crop_land_buffer_size_m = self.marginal_crop_land_buffer_size_m_property,
            marginal_crop_land_slope_threshold_percentage = self.marginal_crop_land_slope_threshold_percentage_property,
            marginal_crop_land_grass_type = self.marginal_crop_land_grass_type_property,
            pasture_crop_land_simulation = self.pasture_crop_land_simulation_property,
            pasture_crop_land_ids=self.pasture_crop_land_landuse_ids_property,
            pasture_crop_land_grass_type=self.pasture_crop_land_grass_type_property
            )

    def generate_parameters(self):
        """watershed delineation""" 
        self.model.generate_parameters(self.get_config_value("reservoir_flow_routing"), 
                                       self.get_config_value("reservoir_flow_data_folder"))

    def update_crop_rotation(self):
        if self.get_config_value("method") == "crop_inventory":
            self.model.update_crop_rotation(
                self.get_config_value("AAFC_crop_inventory_folder"),
                int(self.get_config_value("first_year")),
                int(self.get_config_value("last_year")),                
                bool(self.get_config_value("include_grazing", False))
            )