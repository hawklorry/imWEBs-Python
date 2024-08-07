from imWEBs.imwebs import imWEBs
import logging
logger = logging.getLogger(__name__)

def setup_logger():
    logging.basicConfig(filename=r'C:\Work\imWEBs\test\imwebs.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    setup_logger()
    imwebs = imWEBs(r"C:\Work\imWEBs\test\imwebs_config_tutorial.ini")