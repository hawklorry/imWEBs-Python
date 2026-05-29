from .folder_base import FolderBase
from .names import Names
from .raster_extension import RasterExtension
from .vector_extension import VectorExtension
from whitebox_workflows import Raster, Vector, VectorGeometryType
from .lookup import Lookup
import logging
from .bmp.bmp_type import BMPType
from .bmp.bmp_reach_reservoir import ReachBMPReservoir
from .bmp.bmp_reach_point_source import ReachBMPPointSource
from .bmp.bmp_reach_grass_waterway import ReachBMPGrassWaterWay
from .bmp.bmp_structure_wascob import StructureBMPWascob
from .bmp.bmp_structure_tile_drain import StructureBMPTileDrain
from .bmp.bmp_manure_feedlot_validation import ManureFeedlotCatchBasinStorageValidator
from .database.hydroclimate.hydroclimate_database import HydroClimateDatabase

logger = logging.getLogger(__name__)

class Inputs(FolderBase):
    """
    Info from input folder, these are the original input file with standard name
    """
    def __init__(self, input_folder:str, hydroclimate_database:HydroClimateDatabase = None) -> None:
        super().__init__(input_folder)        

        self.cell_size = self.dem_raster.configs.resolution_x        
        self.cellsize_m2 = self.dem_raster.configs.resolution_x * self.dem_raster.configs.resolution_y
        self.cellsize_km2 = self.cellsize_m2 / 1e6
        self.cellsize_ha = self.cellsize_m2 / 1e4
        self.nodata = self.dem_raster.configs.nodata
        self.rows = self.dem_raster.configs.rows
        self.columns = self.dem_raster.configs.columns
        self.hydroclimate_database = hydroclimate_database
        self.__validate()

    def create_new_raster(self)->Raster:
        return self.wbe.new_raster(self.dem_raster.configs)

#region Watershed

    @property
    def dem_raster(self)->Raster:
        """
        Original DEM Raster
        """
        return self.get_raster(Names.get_standard_file_name("dem_raster"))

    @property
    def landuse_raster(self)->Raster:
        return self.get_raster(Names.get_standard_file_name("landuse_raster"))
    
    @property
    def soil_raster(self)->Raster:
        return self.get_raster(Names.get_standard_file_name("soil_raster"))
    
    @property
    def stream_network_user_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("stream_shapefile"))  
    
    @property
    def boundary_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("boundary_shapefile"))
    
    @property
    def outlet_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("outlet_shapefile"))
  
    @property
    def farm_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("farm_shapefile"))  
    
    @property
    def field_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("field_shapefile")) 

    @property
    def is_farm_same_as_field(self)->bool:
        return self.field_vector is not None and (self.farm_vector is None or Names.get_standard_file_name("farm_shapefile") == Names.get_standard_file_name("field_shapefile"))

#endregion

#region Lookup

    @property
    def soil_lookup_csv(self):
        return self.find_file(Names.get_standard_file_name("soil_lookup"))       
    
    @property
    def landuse_lookup_csv(self):
        return self.find_file(Names.get_standard_file_name("landuse_lookup"))       

#endregion

#region Reach BMP

    @property
    def reach_bmp_vectors(self)->list:
        return [self.point_source_vector, self.flow_diversion_vector, self.reservoir_vector, 
                self.catchbasin_vector, self.access_management_vector,
                self.water_use_vector]

    @property
    def point_source_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("point_source_shapefile")) 

    @property
    def flow_diversion_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("flow_diversion_shapefile")) 

    @property
    def reservoir_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("reservoir_shapefile")) 
    
    @property
    def wetland_boundary_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("wetland_boundary_shapefile"))  
    
    @property
    def wetland_outlet_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("wetland_outlet_shapefile"))       
   
    @property
    def reservoir_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("reservoir_shapefile"))      
   
    @property
    def catchbasin_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_catch_basin_shapefile"))
    
    @property
    def grass_waterway_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("grass_waterway_shapefile"))
    
    @property
    def access_management_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("access_management_shapefile"))
    
    @property
    def water_use_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("water_use_shapefile"))   

#endregion

#region Structure BMP

    @property
    def dugout_boundary_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("dugout_boundary_shapefile"))
    
    @property
    def dugout_outlet_vector(self)->Vector:
        return None

    @property
    def raparian_buffer_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("riparian_buffer_shapefile"))    
    
    @property
    def filter_strip_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("filter_strip_shapefile"))    
    
    @property
    def wascob_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("wascob_shapefile"))
    
    @property
    def tile_drain_boundary_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("tile_drain_boundary_shapefile"))    
    
    @property
    def tile_drain_outlet_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("tile_drain_outlet_shapefile"))    

#endregion

#region areal non-structure bmp

    @property
    def feedlot_boundary_vector(self)->Vector:
        return self.get_vector(Names.feedlotShpName)
    
    @property
    def feedlot_outlet_vector(self)->Vector:
        return self.get_vector(Names.feedlotOutletShpName)
    
    @property
    def manure_storage_boundary_vector(self)->Vector:
        return self.get_vector(Names.manureStorageShpName)
    
    @property
    def offsite_watering_vector(self)->Vector:
        return self.get_vector(Names.offsiteWinteringShpName)

#endregion

#region Marginal & Pasture crop land

    @property
    def marginal_crop_land_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("marginal_crop_land_shapefile"))
    
    @property
    def pasture_crop_land_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("pasture_crop_land_shapefile"))

#endregion

#region Manure Adjustment

    @property
    def manure_adjustment_incorporation_within_48h_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_incorporation_within_48h_shapefile"))

    @property
    def manure_adjustment_application_setback_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_application_setback_shapefile"))
    
    @property
    def manure_adjustment_no_application_on_snow_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_no_application_on_snow_shapefile"))
    
    @property
    def manure_adjustment_spring_rather_than_fall_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_spring_rather_than_fall_shapefile"))
    
    @property
    def manure_adjustment_based_on_n_limit_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_based_on_n_limit_shapefile"))
    
    @property
    def manure_adjustment_based_on_p_limit_vector(self)->Vector:
        return self.get_vector(Names.get_standard_file_name("manure_adjustment_based_on_p_limit_shapefile"))

#endregion

    @property
    def bmp_types(self):
        bmps = []

        #reach bmp
        if self.reservoir_vector is not None:
            bmps.append(BMPType.BMP_TYPE_RESERVOIR)
        if self.flow_diversion_vector is not None:
            bmps.append(BMPType.BMP_TYPE_FLOWDIVERSION_STREAM)
        if self.point_source_vector is not None:
            bmps.append(BMPType.BMP_TYPE_POINTSOURCE)
        if self.wetland_boundary_vector is not None:
            bmps.append(BMPType.BMP_TYPE_WETLAND)
        if self.catchbasin_vector is not None:
            bmps.append(BMPType.BMP_TYPE_MANURE_CATCHBASIN)
        if self.grass_waterway_vector is not None:
            bmps.append(BMPType.BMP_TYPE_GRASSWATERWAY)
        if self.access_management_vector is not None:
            bmps.append(BMPType.BMP_TYPE_ACCESSMGT)
        if self.water_use_vector is not None:
            bmps.append(BMPType.BMP_TYPE_WATERUSE)

        #structure bmp
        if self.dugout_boundary_vector is not None:
            bmps.append(BMPType.BMP_TYPE_DUGOUT)
        if self.wascob_vector is not None:
            bmps.append(BMPType.BMP_TYPE_WASCOB)
        if self.tile_drain_boundary_vector is not None:
            bmps.append(BMPType.BMP_TYPE_TILEDRAIN)
        if self.raparian_buffer_vector is not None:
            bmps.append(BMPType.BMP_TYPE_RIPARIANBUFFER)
        if self.filter_strip_vector is not None:
            bmps.append(BMPType.BMP_TYPE_FILTERSTRIP)

        #non-structure
        if self.manure_storage_boundary_vector is not None:
            bmps.append(BMPType.BMP_TYPE_MANURE_STORAGE)
        if self.feedlot_boundary_vector is not None:
            bmps.append(BMPType.BMP_TYPE_MANURE_FEEDLOT)

        #manure adjustment
        if self.manure_adjustment_incorporation_within_48h_vector is not None:
            bmps.append(BMPType.BMP_TYPE_MI48H)
        if self.manure_adjustment_application_setback_vector is not None:
            bmps.append(BMPType.BMP_TYPE_MSETBACK)
        if self.manure_adjustment_no_application_on_snow_vector is not None:
            bmps.append(BMPType.BMP_TYPE_NO_ONSNOW)
        if self.manure_adjustment_spring_rather_than_fall_vector is not None:
            bmps.append(BMPType.BMP_TYPE_NO_FALL)
        if self.manure_adjustment_based_on_n_limit_vector is not None:
            bmps.append(BMPType.BMP_TYPE_NITROGEN_LIMIT)
        if self.manure_adjustment_based_on_p_limit_vector is not None:
            bmps.append(BMPType.BMP_TYPE_PHOSPHORUS_LIMIT)

        return bmps  

    def __validate(self):
        """
        Validate necessary files are present.
        Validate all grid inputs so they have same dimension. DEM is used as the standard. 
        Only soil and landuse are used here assuming all other inputs are gnereated from shapefile and would correct dimension as the dem.      
        """

        logger.info("Validating inputs ...")

        #check mandatary files
        if self.dem_raster is None:
            raise ValueError("Can't find DEM")
        if self.dem_raster.configs.nodata > -32768:
            raise ValueError("The no data value of dem raster is not valid. Use -32768.")
        
        if self.stream_network_user_vector is None:
            raise ValueError("Can't find user stream network shapefile.")
        
        if self.soil_raster is None:
            raise ValueError("Can't find soil raster")
        if self.soil_raster.configs.nodata > -32768:
            raise ValueError("The no data value of soil raster is not valid. Use -32768.")
        
        if self.landuse_raster is None:
            raise ValueError("Can't find landuse raster")     
        if self.landuse_raster.configs.nodata > -32768:
            raise ValueError("The no data value of landuse raster is not valid. Use -32768.")        
        
        if self.field_vector is None:
            raise ValueError("Can't find field shapefile")   
        VectorExtension.validate_vector_shape_type(self.field_vector, VectorGeometryType.Polygon)

        if self.is_farm_same_as_field:
            logger.info("Farm shapefile is not provided. The field shapefile will be used as the farm field.")
        
        if self.soil_lookup_csv is None:
            raise ValueError("Can't find soil lookup")
        
        if self.landuse_lookup_csv is None:
            raise ValueError("Can't find landuse lookup")

        #Check if dem, soil and landuse has the same dimension
        #All input rasters should have the same dimension
        if not RasterExtension.compare_raster_extent(self.dem_raster, self.soil_raster):
            raise ValueError("The soil raster doesn't have same dimension as dem.")

        if not RasterExtension.compare_raster_extent(self.dem_raster, self.landuse_raster):
            raise ValueError("The landuse raster doesn't have same dimension as dem.")
        
        #valiate bmp inputs to make sure attributes are setup correctly
        self.check_manure_feedlot_catchbasin_storage()
        ReachBMPReservoir.validate(self.reservoir_vector)
        ReachBMPPointSource.validate(self.point_source_vector, self.hydroclimate_database)
        ReachBMPGrassWaterWay.validate(self.grass_waterway_vector)
        StructureBMPWascob.validate(self.wascob_vector)
        StructureBMPTileDrain.validate(self.tile_drain_boundary_vector, self.tile_drain_outlet_vector)

        #check if the soil/lookup raster ids are included in corresponding lookup csv files
        logger.info("Loading lookup tables ...")
        self.lookup_soil =  Lookup(self.soil_lookup_csv, self.soil_raster)
        self.lookup_landuse  = Lookup(self.landuse_lookup_csv, self.landuse_raster)


    def check_manure_feedlot_catchbasin_storage(self):
        """
        Validate manure feedlot/catch basin/storage relationships.

        1. Feedlot boundary has required feedlot fields.
        2. Feedlot outlet ids match feedlot boundary ids.
        3. Feedlot catch basin references exist in catch basin layer.
        4. Manure storage feedlot references exist in feedlot layer.
        """
        ManureFeedlotCatchBasinStorageValidator.validate(
            catch_basin_vector=self.catchbasin_vector,
            feedlot_boundary_vector=self.feedlot_boundary_vector,
            feedlot_outlet_vector=self.feedlot_outlet_vector,
            manure_storage_boundary_vector=self.manure_storage_boundary_vector,
        )
            




