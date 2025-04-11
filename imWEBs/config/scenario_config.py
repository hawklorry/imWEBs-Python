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
from ..model.parameter_h5 import ParameterH5
from ..interpolation.weight_file import WriteWeightFile
from ..outputs import Outputs
from ..model.model import Model
import numpy as np
import shutil
from ..subarea.parameter_subarea import ParameterSubarea

logger = logging.getLogger(__name__)

class ScenarioConfig(Config):
    """Config for scenario creation"""

    def __init__(self, config_file: str = None):
        super().__init__(config_file)

        if config_file is not None:
            self.__load()

    def __load(self):
        """
        load the config file, validate and copy the input files
        """

        if self.config_file is None or not os.path.exists(self.config_file):
            raise ValueError(f"Couldn't find {self.config_file}.")

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
                        if var.upper() == "T":
                            setattr(self, "TMAX", ids)
                            setattr(self, "TMIN", ids)
                            self.data_type_station_ids["TMAX"] = ids
                            self.data_type_station_ids["TMIN"] = ids
                        else:
                            setattr(self, var, ids)
                            self.data_type_station_ids[var] = ids

                    elif (var == "start_date" or var == "end_date") and value is not None and len(value.strip()) > 0:
                        setattr(self, var, pd.Timestamp(value))
                    elif value is not None and len(value.strip()):
                        setattr(self, var, value)

                    if var == "model_folder":
                        if not os.path.exists(value):
                            raise ValueError(f"Model Folder {value} doesn't exist. Please delineate watershed first.")
                        self.model = Model(value)
                        
                    if var == "name":
                        if value is None or len(value) <=0:
                            raise ValueError("Please give a valide scenario name.")
                        self.scenario_folder = os.path.join(self.model_folder, value)
                        if not os.path.exists(self.scenario_folder):
                            os.makedirs(self.scenario_folder)
            self.__validate()

    def __validate(self):
        #set default value for model type and interval
        if self.model_type is None:
            self.model_type = "cell"
        if self.interval is None:
            self.interval = "daily"

        #if user provide ids, we check if the ids are available.
        #if all is empty, we will use all the available ids
        available_stations_dict = self.model.hydroclimate.data_type_station_ids_dictionary
        if len(self.data_type_station_ids) > 0:            
            for datatype, user_ids in self.data_type_station_ids.items():
                station_ids = available_stations_dict[datatype]
                for id in user_ids:
                    if id not in station_ids:
                        raise ValueError(f"Climate Station {id} for Type {datatype} is not available in hydroclimate database.")
        else:
            self.data_type_station_ids = available_stations_dict

        #check start and end date
        #if the start date and end date is not set, use the start and end date from the database
        database_start_date = self.model.hydroclimate.data_start_date
        database_end_date = self.model.hydroclimate.data_end_date
        if self.start_date is not None and self.start_date < database_start_date:
            raise ValueError(f"The earliest date in hydroclimate database is {database_start_date}, earlier than the user specified start date {self.start_date}")
        if self.end_date is not None and self.end_date > database_end_date:
            raise ValueError(f"The latest date in hydroclimate database is {database_end_date}, earlier than the user specified start date {self.end_date}")                
        if self.start_date is None:
            self.start_date = database_start_date
        if self.end_date is None:
            self.end_date = database_end_date

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
            #T is for TMIN and TMAX
            "climate_station":
            [
                "P",
                "T",
                "RM",
                "SR",
                "WS",
                "WD"
            ],

            "climate_interpolation":
            [
                #average_uniform
                #grid_interpolation
                #inverse_distance
                #linear_triangle
                #thiessen_polygon
                "method"
            ]
            }    
    
    def __generate_file_in(self):
        logger.info("Creating file.in ...")
        #get cell size and number of valid cells for cell-based model
        cell_size = -1
        cell_number = -1
        subarea_number = -1
        if self.model_type == "cell":
            cell_size = self.model.outputs.inputs.cell_size
            cell_number = self.model.outputs.number_of_valid_cell
        else:
            subarea_number = self.model.generate_subarea()

        #create file.in
        file_in = FileIn(folder = self.scenario_folder, 
                         model_type=self.model_type, 
                         cell_size=cell_size,
                         cell_num=cell_number,
                         subarea_num=subarea_number,
                         subbasin_num=self.model.outputs.number_of_subbasin,
                         start_date=self.start_date,
                         end_date=self.end_date,
                         data_type_station_ids=self.data_type_station_ids, 
                         interval=self.interval)
        
        file_in.write_file()

    def __generate_file_out(self):
        #create file.out
        logger.info("Creating file.out ...")
        file_out = FileOut(self.scenario_folder)
        file_out.write_file()

    def __generate_config_fig(self):
        #create config.fig
        logger.info("Creating config.fig ...")
        config = ConfigFile(self.scenario_folder)
        config.write_file()

    def __generate_weight_file(self):
        logger.info(f"Creating weight file with method {self.method} ...")
        #create weight files use the climate stations selected by users
        coordinates = self.model.hydroclimate.station_coordinates
        previous_ids = []
        previous_weight_file = ""        
        precipitation_weight_file = ""

        #we will create the weight file in the model output folder to facilitate parameter.h5 generation.
        #we will delete any previous weight file first
        weight_file_folder = self.model.model_output_folder
        for wf in [f for f in os.listdir(weight_file_folder) if "weight" in f and ".txt" in f]:
            os.remove(os.path.join(weight_file_folder, wf))

        #start to write
        for datatype, ids in self.data_type_station_ids.items():             
            #we only need one for temperature so skip for TIMIN 
            #same for wind speed and direction    
            if datatype.upper() == "TMIN" or datatype.upper() == "WD":
                continue            
            
            #get weight file name
            weight_file = f"weight_{datatype.lower()}.txt"
            if datatype.upper() == "TMAX":
                weight_file = "weight_t.txt"
            if datatype.upper() == "WS":
                weight_file = "weight_w.txt"

            logger.info(f"Writing {weight_file}")

            #just copy previous weight file if the stations are the same
            if len(previous_ids) > 0 and np.array_equal(np.sort(previous_ids), np.sort(ids)):
                shutil.copyfile(os.path.join(weight_file_folder, previous_weight_file),os.path.join(weight_file_folder, weight_file))
            else:
                #write the weight file
                WriteWeightFile(self.method, 
                                os.path.join(weight_file_folder, weight_file),
                                self.model.outputs.mask_refined_with_subbasin_raster,
                                [coordinates[id] for id in ids])
            #save it
            previous_ids = ids
            previous_weight_file = weight_file
            if datatype.upper() == "P":
                precipitation_weight_file = weight_file

        #copy weight file p for pet
        if "PET" not in self.data_type_station_ids and len(precipitation_weight_file) > 0:
            logger.info("Writing weight_pet.txt")
            shutil.copyfile(os.path.join(weight_file_folder, precipitation_weight_file),os.path.join(weight_file_folder, "weight_pet.txt"))

    def __generate_parameter_h5(self):
        """
        generate parameter h5 file
        """
        logger.info(f"Creating parameter.h5 ...")
        ParameterH5.generate_parameter_h5(self.scenario_folder, self.model.model_output_folder)

    def __generate_reach_parameter(self):
        """
        Copy/create reach parameter from watershed/output folder.
        It has same structure as the weight file. The header must start with #        
        """
        logger.info(f"Creating reachParameter.txt ...")
        reach_parameter_df = self.model.outputs.reach_parameter_df.copy()

        #write to file
        reach_parameter_file = os.path.join(self.scenario_folder, Names.reachParameterTxtName)
        reach_parameter_file_temp = os.path.join(self.scenario_folder, "temp.txt")
        with open(reach_parameter_file,'w') as f:
            f.writelines(f"{len(reach_parameter_df)}\n{len(reach_parameter_df.columns)}\n#")

            reach_parameter_df.to_csv(reach_parameter_file_temp, sep = "\t", index=False)
            with open(reach_parameter_file_temp,'r') as f_temp:
                f.write(f_temp.read())

        os.remove(reach_parameter_file_temp)
    
    def generate_parameter_subarea_database(self):
        if self.model_type == "subarea":
            p = ParameterSubarea(self.model.outputs)
            p.generate()

    def __generate_bmp_database(self):
        """just copy the bmp database from database folder""" 
        shutil.copy(os.path.join(self.model.model_database_folder, Names.bmpDatabaseName), 
                    os.path.join(self.scenario_folder, Names.bmpDatabaseName))

    def __run_imwebs(self):
        pass

    def generate_model_structure(self):
        """generate model structure"""
        self.__generate_file_in()
        self.__generate_file_out()
        self.__generate_config_fig()
        self.__generate_weight_file()
        self.__generate_parameter_h5()
        self.__generate_reach_parameter() 
        self.generate_parameter_subarea_database()       
        self.__generate_bmp_database()









            



