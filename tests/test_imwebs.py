from imWEBs.imwebs import imWEBs
import logging
import logging.config
from imWEBs.database.parameter.parameter_database import ParameterDatabase
from imWEBs.database.bmp.bmp_database import BMPDatabase
from imWEBs.database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from imWEBs.config.model_config import ModelConfig
from imWEBs.config.scenario_config import ScenarioConfig
from imWEBs.raster_extension import RasterExtension
from imWEBs.vector_extension import VectorExtension
from whitebox_workflows import WbEnvironment
from imWEBs.database.database_base import DatabaseBase
import datetime
import os
import traceback
import h5py
from imWEBs.iuh import IUH

logger = logging.getLogger(__name__)
log_folder = r"C:\Work\imWEBs\test\log"

config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': os.path.join(log_folder, f'imwebs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        },
    },
    'loggers': {
        __name__: {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'detailedLogger': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False,
        },
    }
}

def setup_logger():
    #logging.config.dictConfig(config)
    # logging.basicConfig(filename= os.path.join(log_folder, f'imwebs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'), 
    #                     level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_parameter_database():
    logging.basicConfig(filename=r'C:\Work\imWEBs\test\test_parameter_database\imwebs_parameter_database.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    parameter_db = ParameterDatabase(r"C:\Work\imWEBs\test\test_parameter_database\parameter.db3")

def test_bmp_database():
    logging.basicConfig(filename=r'C:\Work\imWEBs\test\test_bmp_database\imwebs_bmp_database.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    bmp_db = BMPDatabase(r"C:\Work\imWEBs\test\test_bmp_database\bmp.db3")

def test_model():
    imwebs = imWEBs(r"C:\Work\imWEBs\test\imwebs_config_tutorial.ini")

def test_model_config():
    config = ModelConfig()
    config.create_template(r"C:\Work\imWEBs\test\imwebs_config_model.ini")

def test_scenario_config():
    config = ScenarioConfig()
    config.create_template(r"C:\Work\imWEBs\test\imwebs_config_scenario.ini")

def test_mode_parameter_h5():
    config = ScenarioConfig(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\stc\imwebs_config_scenario_stc.ini")
    config.generate_parameter_h5()

def test_mode_structure():
    config = ScenarioConfig(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\stc\imwebs_config_scenario_stc.ini")
    config.generate_model_structure()

def test_hydroclimate_migrate():
    HydroClimateDatabase.migrate(r"C:\Work\imWEBs\Tutorial\data\HydroClimate.db3")

def test_h5():
    with h5py.File(r"C:\Work\imWEBs\Tutorial\model\tutorial\model01\parameter.h5", 'r') as h5_file:
        group = h5_file['asc']
        for attr_name, attr_value in group.attrs.items():
            print(f"Attribute Name: {attr_name}, Attribute Value: {attr_value}")

def test_tile_drain_subbasin():
    wbe = WbEnvironment()

    tile_drain_raster = wbe.read_raster(r"C:\Work\imWEBs\test\gg\watershed\output\tile_drain.tif")
    subbasin_raster = wbe.read_raster(r"C:\Work\imWEBs\test\gg\watershed\output\subbasin.tif")
    dem_raster = wbe.read_raster(r"C:\Work\imWEBs\test\gg\watershed\output\dem.tif")

    #overlay tile drain and subbasin to get the area of the each unique combination.
    tiledrain_subbasin_raster, tile_drain_max_id, _ = RasterExtension.get_overlay_raster(tile_drain_raster, subbasin_raster)
    df_tile_drain_subbasin_overlay_mean_elevation = RasterExtension.get_zonal_statistics(dem_raster, tiledrain_subbasin_raster,"mean") 
    df_tile_drain_subbasin_overlay_mean_elevation.to_csv(r"C:\Work\imWEBs\test\gg\watershed\output\tile_drain_subbasin.csv")

    
    df_tile_drain_subbasin_overlay_mean_elevation["tile_drain"] = df_tile_drain_subbasin_overlay_mean_elevation.index % tile_drain_max_id
    df_tile_drain_subbasin_overlay_mean_elevation.to_csv(r"C:\Work\imWEBs\test\gg\watershed\output\tile_drain_subbasin.csv")

    df_tile_drain_subbasin_overlay_mean_elevation["subbasin"] = (df_tile_drain_subbasin_overlay_mean_elevation.index - df_tile_drain_subbasin_overlay_mean_elevation["tile_drain"]) / tile_drain_max_id
    df_tile_drain_subbasin_overlay_mean_elevation.to_csv(r"C:\Work\imWEBs\test\gg\watershed\output\tile_drain_subbasin.csv")

    #get the rows with max area for each ids in raster 1
    min_elevation_idx = df_tile_drain_subbasin_overlay_mean_elevation.groupby("tile_drain")["mean"].idxmin()        
    df_tile_drain_subbasin_overlay_mean_elevation = df_tile_drain_subbasin_overlay_mean_elevation.loc[min_elevation_idx,["tile_drain","subbasin"]].astype({"tile_drain":"int","subbasin":"int"})
    df_tile_drain_subbasin_overlay_mean_elevation.to_csv(r"C:\Work\imWEBs\test\gg\watershed\output\tile_drain_subbasin_summary.csv")
    #self.__dict_tile_drain_subbasin = df_tile_drain_subbasin_overlay_mean_elevation.set_index("tile_drain")["subbasin"].to_dict()

def test_overlay():
    wbe = WbEnvironment()
    field_rater = wbe.read_raster(r"C:\Work\imWEBs\test\stc\watershed\output\field.tif")
    df = RasterExtension.get_category_area_ha_dataframe(field_rater, "area")


    subarea_rater = wbe.read_raster(r"C:\Work\imWEBs\test\stc\watershed\output\subarea.tif")
    riparian_buffer_rater = wbe.read_raster(r"C:\Work\imWEBs\test\stc\watershed\output\riparian_buffer_part.tif")
    merged_raster, _, _ = RasterExtension.get_overlay_raster(subarea_rater, riparian_buffer_rater)
    vector = RasterExtension.raster_to_vector(merged_raster)
    wbe.write_raster(merged_raster, r"C:\Work\imWEBs\test\stc\watershed\output\subarea_riparian_buffer_part.tif")
    VectorExtension.save_vector(vector,r"C:\Work\imWEBs\test\stc\watershed\output\subarea_riparian_buffer_part.shp")

def test_iuh():
    wbe = WbEnvironment()

    dem_clipped_raster_for_model = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\dem.tif")
    slope_percent_raster = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\slope.tif")
    flow_direction_raster = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\flow_dir.tif")
    flow_acc_raster = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\flow_acc.tif")
    manning_raster = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\manning.tif")
    stream_network_raster = wbe.read_raster(r"C:\Work\imWEBs\Zion\MedwayCreek09March\InterfaceoutputSubarea\watershed\output\stream_network.tif")
    iuh = IUH(dem_clipped_raster_for_model, slope_percent_raster,
                flow_direction_raster, flow_acc_raster, manning_raster,stream_network_raster)
    
    iuh_2yr = iuh.generate_travel_time_average_standard_deviation(
        0.04, 0.45, 3, 0.005)

def test_database():
    db = DatabaseBase(r"C:\Work\imWEBs\test\BMP.db3")
    print(db.check_table("BMP_Index",["ID","name","Type","code"]))

def test_all():
    try:
        # imwebs = imWEBs(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\Garvey_Glenn\imwebs_config_model_gg.ini",
        #              r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\Garvey_Glenn\imwebs_config_scenario_gg.ini")
        
        # imwebs = imWEBs(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\Medway_Creek\imwebs_config_model_MC.ini",
        #             r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\Medway_Creek\imwebs_config_scenario_MC.ini")
   
        imwebs = imWEBs(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\stc\imwebs_config_model_stc.ini",
                     r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\stc\imwebs_config_scenario_stc.ini")
        
        # imwebs = imWEBs(r"C:\Users\hawkl\Downloads\InputData_Oct2025\imwebs_config_model.ini",
        #              r"C:\Users\hawkl\Downloads\InputData_Oct2025\imwebs_config_scenario.ini")

        # imwebs = imWEBs(r"C:\Work\imWEBs\Zion\MedwayCreek09March\imwebs_config_model_mcs.ini",
        #             r"C:\Work\imWEBs\Zion\MedwayCreek09March\imwebs_config_scenario_mcs.ini")
        imwebs.generate_all()
        #imwebs.generate_pour_points_based_on_threshold_and_structures()
        #imwebs.generate_subarea_parameter_database()
        #imwebs.generate_scenario()
        #imwebs.delineate_watershed()
        #imwebs.generate_parameters()
        #raster = imwebs.model_config.model.outputs.soil_porosity_raster
        #imwebs.update_crop_rotation()
        

        # config = ScenarioConfig(r"C:\Work\Git\imWEBs\imWEBs-Python\notebooks\stc\imwebs_config_scenario_stc.ini")
        # config.generate_model_structure()

    except ValueError as ve:
        logger.error(ve)
        logger.error(traceback.format_exc())
    except BaseException as be:
        logger.error(be)
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    setup_logger()
    #test_parameter_database()
    #test_bmp_database()
    #test_model_config()
    #test_scenario_config()
    #test_hydroclimate_migrate()
    test_all()
    #test_database()
    #test_iuh()
    #test_tile_drain_subbasin()
    #test_mode_structure()
    #test_h5()
    #test_overlay()
    
    #cd C:\Work\Git\imWEBs\Engine\WetSpaInterface2\x64\Release>imwebsmain 
    #C:\Work\Git\imWEBs\Engine\WetSpaInterface2\x64\Release\ C:\Work\imWEBs\test\gg\scenario_cell 2

    #select structure_bmp_tile_drain.id, structure_bmp_tile_drain.elevation,reach_parameter.min_elevation - reach_parameter.depth from structure_bmp_tile_drain inner join reach_parameter on structure_bmp_tile_drain.outletreachid = reach_parameter.reach_id


    

    

