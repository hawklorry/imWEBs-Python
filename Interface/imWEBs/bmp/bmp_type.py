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


BMPDistributions = {
    BMPType.BMP_TYPE_POINTSOURCE: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_FLOWDIVERSION_STREAM: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_RESERVOIR: Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_WETLAND:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_MANURE_CATCHBASIN:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_GRASSWATERWAY:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_DUGOUT:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_ACCESSMGT:Names.bmp_table_name_reach_bmp,
    BMPType.BMP_TYPE_WATERUSE:Names.bmp_table_name_reach_bmp,

    BMPType.BMP_TYPE_CROP:Names.bmp_table_name_crop_management,
    BMPType.BMP_TYPE_FERTILIZER:Names.bmp_table_name_fertilizer_management,
    BMPType.BMP_TYPE_TILLAGE:Names.bmp_table_name_tillage_management,
    BMPType.BMP_TYPE_GRAZING:"",
    BMPType.BMP_TYPE_MANURE_STORAGE: Names.bmp_table_name_manure_storage_management,
    BMPType.BMP_TYPE_MANURE_FEEDLOT: Names.bmp_table_name_manure_feed_lot_management        
}

BMPParameters = {
    BMPType.BMP_TYPE_POINTSOURCE: Names.bmp_talbe_name_point_source,
    BMPType.BMP_TYPE_FLOWDIVERSION_STREAM: Names.bmp_talbe_name_flow_diversion,
    BMPType.BMP_TYPE_RESERVOIR: Names.bmp_table_name_reservoir,
    BMPType.BMP_TYPE_WETLAND:Names.bmp_table_name_wetland,
    BMPType.BMP_TYPE_MANURE_CATCHBASIN:Names.bmp_table_name_manure_catch_basin,
    BMPType.BMP_TYPE_GRASSWATERWAY:Names.bmp_table_name_grass_waterway,
    BMPType.BMP_TYPE_DUGOUT:Names.bmp_table_name_dugout,
    BMPType.BMP_TYPE_ACCESSMGT:Names.bmp_table_name_managed_access_including_fencing,
    BMPType.BMP_TYPE_WATERUSE:Names.bmp_table_name_water_use,

    BMPType.BMP_TYPE_CROP:Names.bmp_table_name_crop_parameter,
    BMPType.BMP_TYPE_FERTILIZER:Names.bmp_table_name_fertilizer_parameter,
    BMPType.BMP_TYPE_TILLAGE:Names.bmp_table_name_tillage_parameter,
    BMPType.BMP_TYPE_GRAZING:Names.bmp_table_name_grazing_parameter,
    BMPType.BMP_TYPE_MANURE_STORAGE: Names.bmp_table_name_manure_storage_parameter,
    BMPType.BMP_TYPE_MANURE_FEEDLOT: Names.bmp_table_name_manure_feed_lot_parameter        
}

