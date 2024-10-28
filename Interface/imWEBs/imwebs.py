from .config.model_config import ModelConfig
from .outputs import Outputs

class imWEBs:
    """
    imWEBs main class
    """

    def __init__(self, config_file:str):
        """
        config_file: the imWEBs model configuration file
        """
        self.model_config = ModelConfig(config_file)

    def delineate_watershed(self):
        """
        watershed delineation
        """
        self.model_config.delineate_watershed()

    def generate_parameters(self):
        """
        watershed delineation
        """
        self.model_config.generate_parameters()
        

    def update_crop_rotation(self):
        self.model_config.update_crop_rotation()

    def create_model(self):
        pass

