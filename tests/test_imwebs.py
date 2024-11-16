from imWEBs.imwebs import imWEBs
import logging
import logging.config
from imWEBs.database.parameter.parameter_database import ParameterDatabase
from imWEBs.database.bmp.bmp_database import BMPDatabase
from imWEBs.database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from imWEBs.config.model_config import ModelConfig
from imWEBs.config.scenario_config import ScanrioConfig
import datetime
import os
import traceback
import h5py

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
    config = ScanrioConfig()
    config.create_template(r"C:\Work\imWEBs\test\imwebs_config_scenario.ini")

def test_mode_structure():
    config = ScanrioConfig(r"C:\Work\imWEBs\test\imwebs_config_scenario_tutorial.ini")
    config.generate_model_structure()

def test_hydroclimate_migrate():
    HydroClimateDatabase.migrate(r"C:\Work\imWEBs\Tutorial\data\HydroClimate.db3")

def test_h5():
    with h5py.File(r"C:\Work\imWEBs\Tutorial\model\tutorial\model01\parameter.h5", 'r') as h5_file:
        group = h5_file['asc']
        for attr_name, attr_value in group.attrs.items():
            print(f"Attribute Name: {attr_name}, Attribute Value: {attr_value}")

def test_all():
    try:
        imwebs = imWEBs(r"C:\Work\imWEBs\test\imwebs_config_model_tutorial_all.ini")
        imwebs.delineate_watershed()
        imwebs.generate_parameters()
        imwebs.update_crop_rotation()

        config = ScanrioConfig(r"C:\Work\imWEBs\test\imwebs_config_scenario_tutorial.ini")
        config.generate_model_structure()

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
    #test_mode_structure()
    #test_h5()
    


    

    

