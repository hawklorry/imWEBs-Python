from .config.model_config import ModelConfig
from .config.scenario_config import ScenarioConfig
from .outputs import Outputs

class imWEBs:
    """
    imWEBs main class
    """

    def __init__(self, model_config_file:str, scenario_config_file:str):
        """
        config_file: the imWEBs model configuration file
        """
        self.model_config = ModelConfig(model_config_file)
        self.scenario_config = ScenarioConfig(scenario_config_file)

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
        """
        update crop rotation
        """
        self.model_config.update_crop_rotation()

    def generate_scenario(self):
        self.scenario_config.generate_model_structure()

    def generate_subarea_parameter_database(self):
        self.scenario_config.generate_parameter_subarea_database()

    def generate_all(self):
        self.delineate_watershed()
        self.generate_parameters()
        self.update_crop_rotation()
        self.generate_scenario()

        

