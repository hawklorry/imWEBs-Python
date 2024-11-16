from configparser import ConfigParser
import logging

logger = logging.getLogger(__name__)

class Config:
    """Base class for all configs"""
    def __init__(self, config_file:str = None):
        self.config_file = config_file  
  
    @property
    def config_variables(self)->str:
        return {}

    def create_template(self, file_path:str):
        """
        create a template configuration file with empty values. this file function as the starting point of a working file
        """
        cf = ConfigParser()
        for section, variables in self.config_variables.items():
            cf[section] = {}
            for var in variables:
                cf[section][var] = ""
        with open(file_path, 'w') as configfile:
            cf.write(configfile)

    @staticmethod
    def get_option_value_exactly(cf:ConfigParser, section_name, option_names, valtyp=str):
        """Read the value at the given location as given type"""
        if valtyp == int:
            return cf.getint(section_name, option_names)
        elif valtyp == float:
            return cf.getfloat(section_name, option_names)
        elif valtyp == bool:
            return cf.getboolean(section_name, option_names)
        else:
            return cf.get(section_name, option_names)

    @staticmethod
    def check_config_option(cf, section_name, option_names, print_warn=False):
        """
        check if the config option exist in the config file
        """
        if not isinstance(cf, ConfigParser):
            raise IOError('ErrorInput: The first argument cf MUST be the object of `ConfigParser`!')
        if type(option_names) is not list:
            option_names = [option_names]  

        if section_name not in cf.sections():
            if print_warn:
                logger.warning(f'Warning: Section {section_name} is NOT defined, try to find in DEFAULT section!')
            for optname in option_names:  
                if cf.has_option('', optname): 
                    return True, '', optname
            if print_warn:
                logger.warning(f'Warning: Section {section_name} is NOT defined, Option {option_names} is NOT FOUND!')
            return False, '', ''
        else:
            for optname in option_names:  # For backward compatibility
                if cf.has_option(section_name, optname):
                    return True, section_name, optname
            if print_warn:
                logger.warning(f'Warning: Option {option_names} is NOT FOUND in Section {section_name}!')
            return False, '', ''

    @staticmethod
    def get_option_value(cf, section_name, option_names, valtyp=str, print_warn=True):  
        found, sname, oname = Config.check_config_option(cf, section_name, option_names, print_warn=print_warn)
        if not found:
            return None
        return Config.get_option_value_exactly(cf, sname, oname, valtyp=valtyp)