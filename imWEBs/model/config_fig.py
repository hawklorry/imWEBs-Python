import os
import shutil

class ConfigFile:
    default_file_name = "config.fig"

    def __init__(self, folder) -> None:
        self.folder = folder

    def write_file(self):
        """Just copy the default file for now"""
        default_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults", ConfigFile.default_file_name)
        destination_file = os.path.join(self.folder, ConfigFile.default_file_name)
        shutil.copyfile(default_config_file, destination_file)
        
