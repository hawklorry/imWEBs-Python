from imWEBs.imwebs import imWEBs
import logging
from imWEBs.database.parameter.parameter_database import ParameterDatabase
from imWEBs.database.bmp.bmp_database import BMPDatabase
from imWEBs.database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from imWEBs.config.model_config import ModelConfig
from imWEBs.config.scenario_config import ScanrioConfig
import datetime
import os
import traceback

logger = logging.getLogger(__name__)
log_folder = r"C:\Work\imWEBs\test\log"

def setup_logger():
    logging.basicConfig(filename= os.path.join(log_folder, f'imwebs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'), 
                        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def test_all():
    try:
        imwebs = imWEBs(r"C:\Work\imWEBs\test\imwebs_config_model_tutorial.ini")
        imwebs.delineate_watershed()
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
    test_mode_structure()
    #test_all()


    

    

