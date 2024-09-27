import logging
from .config import Config
from configparser import ConfigParser
import logging
from ..model.file_in import FileIn
from ..model.file_out import FileOut
from ..model.config_fig import ConfigFile
import os
from ..database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from ..names import Names
from datetime import date
import pandas as pd

logger = logging.getLogger(__name__)

class ScanrioConfig(Config):
    """Config for scenario creation"""

    def __init__(self, config_file: str = None):
        super().__init__(config_file)

        if config_file is not None:
            self.__load()

    def __load(self):
        """
        load the config file, validate and copy the input files
        """

        self.data_type_station_ids = {}
        if self.config_file is not None and os.path.exists(self.config_file):           
            logger.info(f"Loading scenario configuration file {self.config_file} ...")
            cf = ConfigParser()
            cf.read(self.config_file)            
            for section, variables in self.config_variables.items():
                for var in variables:
                    value = Config.get_option_value(cf, section, var)  
                    setattr(self, var, None)                  
                    if section == "climate_station" and value is not None and len(value.strip()) > 0:
                        ids = [int(x) for x in value.split(",")]
                        setattr(self, var, ids)
                        self.data_type_station_ids[var] = ids
                    elif (var == "start_date" or var == "end_date") and value is not None and len(value.strip()) > 0:
                        setattr(self, var, pd.Timestamp(value))
                    elif value is not None and len(value.strip()):
                        setattr(self, var, value)

                    if var == "model_folder":
                        if not os.path.exists(value):
                            raise ValueError(f"Model Folder {value} doesn't exist. Please delineate watershed first.")
                        
                    if var == "name":
                        if value is None or len(value) <=0:
                            raise ValueError("Please give a valide scenario name.")
                        self.scenario_folder = os.path.join(self.model_folder, value)
                        if not os.path.exists(self.scenario_folder):
                            os.makedirs(self.scenario_folder)
            self.__validate()

    def __validate(self):
        """make sure all station ids are included in the hdyroclimate database"""
        hydroclimate = HydroClimateDatabase(os.path.join(self.model_folder, "database",Names.hydroclimateDatabasename))

        #if user provide ids, we check if the ids are available.
        #if all is empty, we will use all the available ids
        available_stations_dict = hydroclimate.data_type_station_ids_dictionary
        if len(self.data_type_station_ids) > 0:            
            for datatype, user_ids in self.data_type_station_ids.items():
                station_ids = available_stations_dict[datatype]
                for id in user_ids:
                    if id not in station_ids:
                        raise ValueError(f"Climate Station {id} for Type {datatype} is not available in hydroclimate database.")
        else:
            self.data_type_station_ids = available_stations_dict
                    
        #check start and end date
        database_start_date = hydroclimate.data_start_date
        database_end_date = hydroclimate.data_end_date
        if self.start_date is not None and self.start_date < database_start_date:
            raise ValueError(f"The earliest date in hydroclimate database is {database_start_date}, earlier than the user specified start date {self.start_date}")
        if self.end_date is not None and self.end_date > database_end_date:
            raise ValueError(f"The latest date in hydroclimate database is {database_end_date}, earlier than the user specified start date {self.end_date}")                
        if self.start_date is None:
            self.start_date = database_start_date
        if self.end_date is None:
            self.end_date = database_end_date


    # @property
    # def model_folder(self):
    #     return getattr(self,"model_folder")
    
    # @property
    # def model_type(self):
    #     return getattr(self,"model_type")   
    
    # @property
    # def start_date(self):
    #     return getattr(self,"start_date")   
    
    # @property
    # def end_date(self):
    #     return getattr(self,"end_date")   
    
    # @property
    # def interval(self):
    #     return getattr(self,"interval")   

    @property
    def config_variables(self)->str:
        return {
            #model folder
            "model":["model_folder"],
            
            "scenario":
            [
                "name",        #scenario name will be used as the folder name 
                "model_type",  #cell or subarea based
                "interval",    #daily or hourly
                "start_date",  #empty means use the start date from hydroclimate
                "end_date"     #empty means use the end date from hydroclimate 
            ],

            #climate stations
            #the ids of each station should be given here seperated with comma. 
            #The ids should match the ids in hydroclimate database which will be enforced
            #Exmaple:1,2,3,4
            #Empty means use all the stations for that type. 
            "climate_station":
            [
                "P",
                "TMAX",
                "TMIN",
                "RM",
                "SR",
                "WS",
                "WD"
            ]
            }    
    
    def generate_model_structure(self):
        """generate model structure"""

        #create file.in
        file_in = FileIn(folder = self.scenario_folder, 
                         model_type=self.model_type, 
                         cell_size=30,
                         cell_num=30,
                         subarea_num=30,
                         subbasin_num=40,
                         start_date=self.start_date,
                         end_date=self.end_date,
                         data_type_station_ids=self.data_type_station_ids, 
                         interval=self.interval)
        
        file_in.write_file()

        #create file.out
        file_out = FileOut(self.scenario_folder)
        file_out.write_file()

        #create config.fig
        config = ConfigFile(self.scenario_folder)
        config.write_file()

