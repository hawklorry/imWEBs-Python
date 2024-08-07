from .folder_base import FolderBase
from .names import Names
from .raster_extension import RasterExtension
from whitebox_workflows import Raster, Vector
from .lookup import Lookup

class Inputs(FolderBase):
    """
    Info from input folder, these are the original input file with standard name
    """
    def __init__(self, input_folder:str) -> None:
        super().__init__(input_folder)

        self.__validate()

        self.cell_size = self.dem_raster.configs.resolution_x        
        self.cellsize_m2 = self.dem_raster.configs.resolution_x * self.dem_raster.configs.resolution_y
        self.cellsize_km2 = self.cellsize_m2 / 1e6
        self.cellsize_ha = self.cellsize_m2 / 1e4
        self.nodata = self.dem_raster.configs.nodata
        self.rows = self.dem_raster.configs.rows
        self.columns = self.dem_raster.configs.columns

    def create_new_raster(self)->Raster:
        self.wbe.new_raster(self.dem_raster.configs)

    @property
    def dem_raster(self)->Raster:
        """
        Original DEM Raster
        """
        return self.get_raster(Names.demName)

    @property
    def landuse_raster(self)->Raster:
        return self.get_raster(Names.landuseName)
    
    @property
    def soil_raster(self)->Raster:
        return self.get_raster(Names.soilName)
    
    @property
    def stream_network_user_vector(self)->Vector:
        return self.get_vector(Names.streamNetworUserShpName)  
    
    @property
    def boundary_vector(self)->Vector:
        return self.get_vector(Names.boundaryShpName)
    
    @property
    def outlet_vector(self)->Vector:
        return self.get_vector(Names.outletName)
  
    @property
    def farm_vector(self)->Vector:
        return self.get_vector(Names.farmShpName)  
    
    @property
    def field_vector(self)->Vector:
        return self.get_vector(Names.fieldShpName) 

    @property
    def soil_lookup_csv(self):
        return self.find_file(Names.soilLookupName)       
    
    @property
    def landuse_lookup_csv(self):
        return self.find_file(Names.landuseLookupName)   
    
    @property
    def wetland_boundary_vector(self)->Vector:
        return self.get_vector(Names.wetlandShpName)  
    
    @property
    def wetland_outlet_vector(self)->Vector:
        return self.get_vector(Names.wetlandOutletsUserShpName)  

    @property
    def reservoir_vector(self)->Vector:
        return self.get_vector(Names.reservoirShpName)  

    @property
    def feedlot_boundary_vector(self)->Vector:
        return self.get_vector(Names.feedlotShpName)
    
    @property
    def feedlot_outlet_vector(self)->Vector:
        return self.get_vector(Names.feedlotOutletUserShpName)

    @property
    def catchbasin_boundary_vector(self)->Vector:
        return self.get_vector(Names.catchbasinShpName)
    
    @property
    def catchbasin_outlet_vector(self)->Vector:
        return self.get_vector(Names.catchbasinOutletUserShpName)
    
    @property
    def manure_storage_boundary_vector(self)->Vector:
        return self.get_vector(Names.manureStorageShpName)
    
    @property
    def manure_storage_outlet_vector(self)->Vector:
        return self.get_vector(Names.manureStorageOutletUserShpName)
    
    @property
    def dugout_boundary_vector(self)->Vector:
        return self.get_vector(Names.dugoutShpName)
    
    @property
    def dugout_outlet_vector(self)->Vector:
        return self.get_vector(Names.dugoutOutletUserShpName)
    
    @property
    def wintering_site_vector(self)->Vector:
        return self.get_vector(Names.winteringSiteShpName)

    @property
    def vegetation_filter_strip_vector(self)->Vector:
        return self.get_vector(Names.vegetationFilterStripShpName)
    
    @property
    def riparian_buffer_strip_vector(self)->Vector:
        return self.get_vector(Names.riparianBufferStripShpName)
    
    @property
    def pasture_grazing_strip_vector(self)->Vector:
        return self.get_vector(Names.pastureGrazingShpName)
        
    @property
    def offsite_wintering_vector(self)->Vector:
        return self.get_vector(Names.offsiteWinteringShpName)
    
    def __validate(self):
        """
        Validate necessary files are present.
        Validate all grid inputs so they have same dimension. DEM is used as the standard. 
        Only soil and landuse are used here assuming all other inputs are gnereated from shapefile and would correct dimension as the dem.      
        """

        #check mandatary files
        if self.dem_raster is None:
            raise ValueError("Can't find DEM")
        
        if self.stream_network_user_vector is None:
            raise ValueError("Can't find user stream network shapefile.")
        
        if self.soil_raster is None:
            raise ValueError("Can't find soil raster")
        
        if self.landuse_raster is None:
            raise ValueError("Can't find landuse raster")       
        
        if self.farm_raster is None:
            raise ValueError("Can't find farm raster")       
        
        if self.field_raster is None:
            raise ValueError("Can't find field raster")   
        
        if self.soil_lookup is None:
            raise ValueError("Can't find soil lookup")
        
        if self.landuse_lookup is None:
            raise ValueError("Can't find landuse lookup")

        #Check if dem, soil and landuse has the same dimension
        #All input rasters should have the same dimension
        if not RasterExtension.compare_raster_extent(self.dem_raster, self.soil_raster):
            raise ValueError("The soil raster doesn't have same dimension as dem.")

        if not RasterExtension.compare_raster_extent(self.dem_raster, self.landuse_raster):
            raise ValueError("The landuse raster doesn't have same dimension as dem.")
        
        #check if the soil/lookup raster ids are included in corresponding lookup csv files
        self.lookup_soil =  Lookup(self.soil_lookup_csv, self.soil_raster)
        self.lookup_landuse  = Lookup(self.landuse_lookup_csv, self.landuse_raster)


