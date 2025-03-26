from enum import Enum
from ..names import Names

class BMPType(Enum):
    """The code will be the one used in the database"""
    BMP_TYPE_POINTSOURCE = 1
    BMP_TYPE_FLOWDIVERSION_STREAM = 2
    BMP_TYPE_RESERVOIR = 3
    BMP_TYPE_RIPARIANWETLAND = 4
    BMP_TYPE_RIPARIANBUFFER = 5
    BMP_TYPE_GRASSWATERWAY = 6
    BMP_TYPE_FILTERSTRIP = 7
    BMP_TYPE_POND = 8
    BMP_TYPE_WETLAND = 9
    BMP_TYPE_TERRACE = 10
    BMP_TYPE_FLOWDIVERSION_OVERLAND = 11
    BMP_TYPE_CROP = 12
    BMP_TYPE_RESIDUAL = 13
    BMP_TYPE_TILLAGE = 14
    BMP_TYPE_FERTILIZER = 15
    BMP_TYPE_GRAZING = 16
    BMP_TYPE_PESTICIDE = 17
    BMP_TYPE_IRRIGATION = 18
    BMP_TYPE_TILEDRAIN = 19
    BMP_TYPE_URBAN = 20
    BMP_TYPE_MI48H = 21
    BMP_TYPE_MSETBACK = 22
    BMP_TYPE_NO_ONSNOW = 23
    BMP_TYPE_NO_FALL = 24
    BMP_TYPE_NITROGEN_LIMIT = 25
    BMP_TYPE_PHOSPHORUS_LIMIT = 26
    BMP_TYPE_MANURE_STORAGE = 27
    BMP_TYPE_MANURE_CATCHBASIN = 28
    BMP_TYPE_MANURE_FEEDLOT = 29
    BMP_TYPE_CROP_MAR = 30
    BMP_TYPE_FERTILIZER_MAR = 31
    BMP_TYPE_TILLAGE_MAR = 32
    BMP_TYPE_WINTERING_SITE = 33
    BMP_TYPE_CROP_PS = 34
    BMP_TYPE_FERTILIZER_PS = 35
    BMP_TYPE_TILLAGE_PS = 36
    BMP_TYPE_GRAZING_PS = 37
    BMP_TYPE_DUGOUT = 38
    BMP_TYPE_OFFSITEWATERING = 39
    BMP_TYPE_ACCESSMGT = 40
    BMP_TYPE_WASCOB = 41
    BMP_TYPE_WATERUSE = 42

ReachBMPColumnNames = {
    BMPType.BMP_TYPE_POINTSOURCE: "PointSource",
    BMPType.BMP_TYPE_FLOWDIVERSION_STREAM: "FlowDiversion",
    BMPType.BMP_TYPE_RESERVOIR: "Reservoir",
    BMPType.BMP_TYPE_WETLAND:"Wetland",
    BMPType.BMP_TYPE_MANURE_CATCHBASIN:"CatchBasin",
    BMPType.BMP_TYPE_GRASSWATERWAY:"GrassWaterway",
    BMPType.BMP_TYPE_ACCESSMGT:"AccessManagement",
    BMPType.BMP_TYPE_WATERUSE:"WaterUse"
}

ArealNonStructureBMPs = [
    BMPType.BMP_TYPE_CROP,
    BMPType.BMP_TYPE_FERTILIZER,
    BMPType.BMP_TYPE_TILLAGE,
    BMPType.BMP_TYPE_GRAZING,
    BMPType.BMP_TYPE_MANURE_STORAGE,
    BMPType.BMP_TYPE_MANURE_FEEDLOT
]

ArealStructureBMPs = [
    BMPType.BMP_TYPE_DUGOUT,
    BMPType.BMP_TYPE_RIPARIANBUFFER,
    BMPType.BMP_TYPE_FILTERSTRIP,
    BMPType.BMP_TYPE_TILEDRAIN,
    BMPType.BMP_TYPE_WASCOB
]

#bmp distribution
BMPDistributions = {
    #reach bmps use the same distriubtion table reach_bmp
    BMPType.BMP_TYPE_POINTSOURCE: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_FLOWDIVERSION_STREAM: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_RESERVOIR: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_WETLAND:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_MANURE_CATCHBASIN:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_GRASSWATERWAY:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_DUGOUT:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_ACCESSMGT:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_WATERUSE:Names.bmp_table_name_reach_bmp,

    #non-structure:[distribution_raster_name_in_hdf5]/[management_table_name]
    #use field for crop, fertilizer, tillage and grazing
    BMPType.BMP_TYPE_CROP:f"{Names.remove_extension_from_raster_file(Names.fieldRasName)}/{Names.bmp_table_name_crop_management}",
    BMPType.BMP_TYPE_FERTILIZER:f"{Names.remove_extension_from_raster_file(Names.fieldRasName)}/{Names.bmp_table_name_fertilizer_management}",
    BMPType.BMP_TYPE_TILLAGE:f"{Names.remove_extension_from_raster_file(Names.fieldRasName)}/{Names.bmp_table_name_tillage_management}",
    BMPType.BMP_TYPE_CROP_MAR:f"{Names.remove_extension_from_raster_file(Names.marginalCroplandSeparatedFieldRasName)}/{Names.bmp_table_name_marginal_crop_management}",
    BMPType.BMP_TYPE_FERTILIZER_MAR:f"{Names.remove_extension_from_raster_file(Names.marginalCroplandSeparatedFieldRasName)}/{Names.bmp_table_name_marginal_fertilizer_management}",
    BMPType.BMP_TYPE_TILLAGE_MAR:f"{Names.remove_extension_from_raster_file(Names.marginalCroplandSeparatedFieldRasName)}/{Names.bmp_table_name_marginal_tillage_management}",
    BMPType.BMP_TYPE_GRAZING:f"{Names.remove_extension_from_raster_file(Names.fieldRasName)}/{Names.bmp_table_name_grazing_management}",
    BMPType.BMP_TYPE_MANURE_STORAGE: f"{Names.remove_extension_from_raster_file(Names.manureStorageRasName)}/{Names.bmp_table_name_manure_storage_management}",
    BMPType.BMP_TYPE_MANURE_FEEDLOT: f"{Names.remove_extension_from_raster_file(Names.feedlotBoundaryProcessedRasName)}/{Names.bmp_table_name_manure_feed_lot_management}",     

    #structure
    #riparian buffer and filter strip has two distribution raster: part and drainage
    #other structure bmps have only one distribution raster
    BMPType.BMP_TYPE_RIPARIANBUFFER: f"{Names.remove_extension_from_raster_file(Names.riparianBufferPartRasterName)}/{Names.remove_extension_from_raster_file(Names.riparianBufferDrainageRasterName)}",  
    BMPType.BMP_TYPE_FILTERSTRIP: f"{Names.remove_extension_from_raster_file(Names.filterStripPartRasterName)}/{Names.remove_extension_from_raster_file(Names.filterStripDrainageRasterName)}", 
    BMPType.BMP_TYPE_DUGOUT:Names.remove_extension_from_raster_file(Names.dugoutRasName),
    BMPType.BMP_TYPE_WASCOB:Names.remove_extension_from_raster_file(Names.wascobDrainageAreaRasName),
    BMPType.BMP_TYPE_TILEDRAIN:Names.remove_extension_from_raster_file(f"{Names.tileDrainRasName}/{Names.bmp_table_name_subarea_tile_drain_drainage_lookup}"),


    #manure application adjustment:[distribution_raster_name_in_hdf5]/[management_table_name]
    #they may share the same distribution raster, maybe field?
    BMPType.BMP_TYPE_MI48H :  f"{Names.remove_extension_from_raster_file(Names.manure48hRasName)}/{Names.bmp_table_name_manure_incorporation_within_48h_management}",
    BMPType.BMP_TYPE_MSETBACK :  f"{Names.remove_extension_from_raster_file(Names.manureSetbackRasName)}/{Names.bmp_table_name_manure_application_setback_management}",
    BMPType.BMP_TYPE_NO_ONSNOW :  f"{Names.remove_extension_from_raster_file(Names.manureNoOnSnowRasName)}/{Names.bmp_table_name_manure_no_application_on_snow_management}",
    BMPType.BMP_TYPE_NO_FALL :  f"{Names.remove_extension_from_raster_file(Names.manureSpringRasName)}/{Names.bmp_table_name_manure_spring_application_rather_than_fall_application_management}",
    BMPType.BMP_TYPE_NITROGEN_LIMIT :  f"{Names.remove_extension_from_raster_file(Names.manureNLimitRasname)}/{Names.bmp_table_name_manure_application_based_on_soil_nitrogen_limit_management}",
    BMPType.BMP_TYPE_PHOSPHORUS_LIMIT :  f"{Names.remove_extension_from_raster_file(Names.manurePLimitRasname)}/{Names.bmp_table_name_manure_application_based_on_soil_phosphorous_limit_management}"
}

#bmp parameters
BMPParameters = {
    #reach bmps
    BMPType.BMP_TYPE_POINTSOURCE: Names.bmp_table_name_point_source,
    BMPType.BMP_TYPE_FLOWDIVERSION_STREAM: Names.bmp_table_name_flow_diversion,
    BMPType.BMP_TYPE_RESERVOIR: Names.bmp_table_name_reservoir,
    BMPType.BMP_TYPE_WETLAND:Names.bmp_table_name_wetland,
    BMPType.BMP_TYPE_MANURE_CATCHBASIN:Names.bmp_table_name_manure_catch_basin,
    BMPType.BMP_TYPE_GRASSWATERWAY:Names.bmp_table_name_grass_waterway,
    BMPType.BMP_TYPE_DUGOUT:Names.bmp_table_name_dugout,
    BMPType.BMP_TYPE_ACCESSMGT:Names.bmp_table_name_managed_access_including_fencing,
    BMPType.BMP_TYPE_WATERUSE:Names.bmp_table_name_water_use,

    #non-structure
    #all non-structure bmps has only one parameter table except grazing which has three parameter table:[livestock_parameter]/[fertilizer_parameter]/[offsite_watering_parameter]
    BMPType.BMP_TYPE_CROP:Names.bmp_table_name_crop_parameter,
    BMPType.BMP_TYPE_FERTILIZER:Names.bmp_table_name_fertilizer_parameter,
    BMPType.BMP_TYPE_TILLAGE:Names.bmp_table_name_tillage_parameter,    
    BMPType.BMP_TYPE_CROP_MAR:Names.bmp_table_name_crop_parameter,
    BMPType.BMP_TYPE_FERTILIZER_MAR:Names.bmp_table_name_fertilizer_parameter,
    BMPType.BMP_TYPE_TILLAGE_MAR:Names.bmp_table_name_tillage_parameter,   
    BMPType.BMP_TYPE_MANURE_STORAGE: Names.bmp_table_name_manure_storage_parameter,
    BMPType.BMP_TYPE_MANURE_FEEDLOT: Names.bmp_table_name_manure_feed_lot_parameter,
    BMPType.BMP_TYPE_GRAZING: f"{Names.bmp_table_name_livestock_parameter}/{Names.bmp_table_name_fertilizer_parameter}/{Names.bmp_table_name_offsite_watering}",

    #structure
    BMPType.BMP_TYPE_RIPARIANBUFFER: f"{Names.bmp_table_name_riparian_buffer}/{Names.bmp_table_name_crop_remove_parameter}",
    BMPType.BMP_TYPE_FILTERSTRIP: f"{Names.bmp_table_name_filter_strip}/{Names.bmp_table_name_crop_remove_parameter}",
    BMPType.BMP_TYPE_DUGOUT: Names.bmp_table_name_dugout,
    BMPType.BMP_TYPE_WASCOB:Names.bmp_table_name_wascob,
    BMPType.BMP_TYPE_TILEDRAIN:Names.bmp_table_name_tile_drain,

    #manure application adjustment
    #there is no parameter tables for maure application adjustment bmps
    BMPType.BMP_TYPE_MI48H: "",
    BMPType.BMP_TYPE_MSETBACK: "",
    BMPType.BMP_TYPE_NO_ONSNOW: "",
    BMPType.BMP_TYPE_NO_FALL : "",
    BMPType.BMP_TYPE_NITROGEN_LIMIT: "",
    BMPType.BMP_TYPE_PHOSPHORUS_LIMIT: ""

}

DefaultScenarioId = 2