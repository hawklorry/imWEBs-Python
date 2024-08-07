from .imwebs_config import imWEBsConfig
from .outputs import Outputs

class imWEBs:
    """
    imWEBs main class
    """

    def __init__(self, config_file:str):
        """
        config_file: the imWEBs model configuration file
        """
        self.config = imWEBsConfig(config_file)

    def delineate(self):
        """
        watershed delineation
        """
        pass  

