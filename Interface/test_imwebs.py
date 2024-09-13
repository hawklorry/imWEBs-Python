from imWEBs.imwebs import imWEBs
import logging
from imWEBs.database.parameter.parameter_database import ParameterDatabase
from imWEBs.database.bmp.bmp_database import BMPDatabase
from imWEBs.config.model_config import ModelConfig
import datetime
import os

logger = logging.getLogger(__name__)
log_folder = r"C:\Work\imWEBs\test\log"

def setup_logger():
    logging.basicConfig(filename= os.path.join(log_folder, f'imwebs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'), level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

if __name__ == '__main__':
    setup_logger()
    #test_parameter_database()
    #test_bmp_database()
    #test_model_config()

    try:
        imwebs = imWEBs(r"C:\Work\imWEBs\test\imwebs_config_model_tutorial.ini")
        imwebs.delineate_watershed()
    except ValueError as ve:
        logger.error(ve)
    except:
        pass
    

    

