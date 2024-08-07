from configparser import ConfigParser
import os
from whitebox_workflows import WbEnvironment
from .raster_extension import RasterExtension
from .vector_extension import VectorExtension
from .names import Names
from .outputs import Outputs
import shutil
import logging

logger = logging.getLogger(__name__)

class imWEBsConfig:
    """
    imWEBs config file
    """

    #name of all sections and options
    config_variables = {
        "default":["input_folder"],
        "watershed":["dem_raster","soil_raster","landuse_raster",
                 "stream_shapefile","boundary_shapefile","farm_shapefile",
                 "field_shapefile","outlet_shapefile"],
        "lookup":["soil_lookup","landuse_lookup"],
        "database":["hydroclimate","bmp","parameter"],
        "wetland":["wetland_boundary_shapefile","wetland_outlet_shapefile"],
        "reservoir":["reservoir_shapefile"],
        "livestock":["feedlot_boundary_shapefile", "feedlot_outlet_shapefile",
                     "catchbasin_boundary_shapefile", "catchbasin_outlet_shapefile",
                     "manure_storage_boundary_shapefile", "manure_storage_outlet_shapefile",
                     "riparian_buffer_trip_shapefile",
                     "wintering_site_shapefile",
                     "vegetation_filter_shapefile",
                     "pasture_grazing_shapefile",
                     "dugout_boundary_shapefile","dugout_outlet_shapefile",
                     "offsite_watering_shapefile"],
        "delineation":["stream_threshold_area_ha",
                       "wetland_min_area_ha",
                       "wetland_riparian_contribution_area_ha",
                       "wetland_stream_buffer_distance_m"],
        "model":["model_folder"]
    }

    #the sections that are files
    file_sections = ["watershed","lookup","database","wetland","reservoir","livestock"]

    #standard names
    standard_names = {
        "dem_raster": Names.demName,
        "soil_raster": Names.soilName,
        "landuse_raster": Names.landuseName,
        "stream_shapefile": Names.streamNetworUserShpName,
        "boundary_shapefile": Names.boundaryShpName,
        "farm_shapefile": Names.farmShpName,
        "field_shapefile": Names.fieldShpName,
        "outlet_shapefile": Names.outletName,
        "soil_lookup":Names.soilLookupName,
        "landuse_lookup":Names.landuseLookupName,
        "hydroclimate":Names.hydroclimateDatabasename,
        "bmp": Names.bmpDatabaseName,
        "parameter": Names.parameterDatabaseName,

        "wetland_boundary_shapefile": Names.wetlandShpName,
        "wetland_outlet_shapefile": Names.wetlandOutletsUserShpName,

        "reservoir_shapefile":Names.reservoirShpName, #point shapefile

        "feedlot_boundary_shapefile": Names.feedlotShpName, 
        "feedlot_outlet_shapefile":Names.feedlotOutletUserShpName,

        "catchbasin_boundary_shapefile": Names.catchbasinShpName,
        "catchbasin_outlet_shapefile":Names.catchbasinOutletUserShpName,

        "manure_storage_boundary_shapefile": Names.manureStorageShpName, 
        "manure_storage_outlet_shapefile":Names.manureStorageOutletUserShpName,        

        "wintering_site_shapefile": Names.winteringSiteShpName,

        "vegetation_filter_shapefile": Names.vegetationFilterStripShpName,
        "riparian_buffer_trip_shapefile":Names.riparianBufferStripShpName,

        "pasture_grazing_shapefile":Names.pastureGrazingShpName,

        "dugout_boundary_shapefile":Names.dugoutShpName,
        "dugout_outlet_shapefile": Names.dugoutOutletUserShpName,
        
        "offsite_watering_shapefile": Names.offsiteWinteringShpName #point
    }

    def __init__(self, config_file:str = None):
        self.config_file = config_file
        self.is_valid = True 
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

            cf = ConfigParser()
            cf.read(self.config_file)
            for section, variables in imWEBsConfig.config_variables.items():
                for var in variables:
                    logger.debug(f"Section: {section}, Variable: {var}")
                    if section == "delineation":
                        value = imWEBsConfig.get_option_value_exactly(cf, section, var, valtyp=float)
                        setattr(self, var, value)
                        continue
                    else:
                        value = imWEBsConfig.get_option_value(cf, section, var)
                        setattr(self, var, value)

                    if value is None or len(value) <= 0:
                        continue

                    #check input folder
                    if var == "input_folder":
                        if os.path.exists(value):
                            self.input_folder = value
                        else:
                            file_exist_valid = False
                            logger.warning(f"{var} = {value} doesn't exist!")
                            break
                    
                    #create model folder
                    if var == "model_folder":
                        self.model_folder = value
                        if not os.path.exists(value):
                            os.makedirs(value)
                        continue

                    if section in imWEBsConfig.file_sections:
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

            raster_valid = RasterExtension.compare_rasters(rasters)
            vector_valid = VectorExtension.compare_vectors(vectors)
            self.is_valid = file_exist_valid and raster_valid and vector_valid

            #copy all the input files to the model folder with standard name
            if self.is_valid:
                self.__create_model_folder()

                for option, raster in rasters.items():
                    wbe.write_raster(raster, os.path.join(self.model_input_folder, imWEBsConfig.standard_names[option]))
                for option, vector in vectors.items():
                    VectorExtension.save_vector(vector, os.path.join(self.model_input_folder, imWEBsConfig.standard_names[option]))
                for option, databae_file in databases.items():
                    shutil.copyfile(os.path.join(self.input_folder, databae_file), os.path.join(self.model_database_folder, imWEBsConfig.standard_names[option]))
                for option, lookup_file in lookups.items():
                    shutil.copyfile(os.path.join(self.input_folder, lookup_file), os.path.join(self.model_input_folder, imWEBsConfig.standard_names[option]))

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
  
    @staticmethod
    def create_template(file_path:str):
        """
        create a template configuration file with empty values. this file function as the starting point of a working file
        """
        cf = ConfigParser()
        for section, variables in imWEBsConfig.config_variables.items():
            cf[section] = {}
            for var in variables:
                cf[section][var] = ""
        with open(file_path, 'w') as configfile:
            cf.write(configfile)

    @staticmethod
    def get_option_value_exactly(cf:ConfigParser, section_name, option_names, valtyp=str):
        if valtyp == int:
            return cf.getint(section_name, option_names)
        elif valtyp == float:
            return cf.getfloat(section_name, option_names)
        elif valtyp == bool:
            return cf.getboolean(section_name, option_names)
        else:
            return cf.get(section_name, option_names)

    @staticmethod
    def check_config_option(cf, section_name, option_names, print_warn=False):
        """
        check if the config option exist in the config file
        """
        if not isinstance(cf, ConfigParser):
            raise IOError('ErrorInput: The first argument cf MUST be the object of `ConfigParser`!')
        if type(option_names) is not list:
            option_names = [option_names]  

        if section_name not in cf.sections():
            if print_warn:
                logger.warning(f'Warning: Section {section_name} is NOT defined, try to find in DEFAULT section!')
            for optname in option_names:  
                if cf.has_option('', optname): 
                    return True, '', optname
            if print_warn:
                logger.warning(f'Warning: Section {section_name} is NOT defined, Option {option_names} is NOT FOUND!')
            return False, '', ''
        else:
            for optname in option_names:  # For backward compatibility
                if cf.has_option(section_name, optname):
                    return True, section_name, optname
            if print_warn:
                logger.warning(f'Warning: Option {option_names} is NOT FOUND in Section {section_name}!')
            return False, '', ''

    @staticmethod
    def get_option_value(cf, section_name, option_names, valtyp=str, print_warn=True):  
        found, sname, oname = imWEBsConfig.check_config_option(cf, section_name, option_names, print_warn=print_warn)
        if not found:
            return None
        return imWEBsConfig.get_option_value_exactly(cf, sname, oname, valtyp=valtyp)
    

if __name__ == "__main__":
    #imWEBsConfig.create_template(r"C:\Work\imWEBs\test\imwebs_config_template.ini")
    config = imWEBsConfig(r"C:\Work\imWEBs\test\imwebs_config_tutorial.ini")
    print(config)