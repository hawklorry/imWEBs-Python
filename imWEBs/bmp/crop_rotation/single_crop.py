from whitebox_workflows import Raster
from ...raster_extension import RasterExtension
from ..bmp_type import DefaultScenarioId
import pandas as pd
import numpy as np
import os

import logging
logger = logging.getLogger(__name__)

class SingleCrop():
    def __init__(self, 
                 location_raster: Raster,
                 crop_id:int,
                 scenario:int = DefaultScenarioId):

        self.__crop_management_df = None
        self.__fertilizer_management_df = None
        self.__tillage_management_df = None
        self.__default_setup_dfs = {}
        self.scenario = scenario
        self.crop_id = crop_id
        self.locations = RasterExtension.get_unique_values(location_raster)

    def __get_default_file_path(self, file_name)->str:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        if not os.path.exists(file_path):
            raise ValueError(f"{file_path} doesn't exist. Please check the crop rotation folder.")
        
        return file_path

    def __get_default_setup_df(self, file_name:str)->pd.DataFrame:
        if file_name not in self.__default_setup_dfs:
            df = pd.read_csv(self.__get_default_file_path(file_name))  
            self.__default_setup_dfs[file_name] = df[df["id"] == self.crop_id]

            if len(self.__default_setup_dfs[file_name]) == 0:
                raise ValueError(f"Crop {self.crop_id} is not included in {file_name}. ")

        return self.__default_setup_dfs[file_name]

    @property
    def crop_management_df(self)->pd.DataFrame:
        if self.__crop_management_df  is None:
            default_crop_management_df = self.__get_default_setup_df("default_crop_management.csv")            
            
            repeated_df = default_crop_management_df.loc[default_crop_management_df.index.repeat(len(self.locations))].reset_index(drop=True)
            repeated_df["Location"] = np.sort(np.tile(self.locations, len(default_crop_management_df)))
            repeated_df["Scenario"] = self.scenario
            repeated_df['ID'] = repeated_df['Location']
            repeated_df['ActualYear'] = 0
            repeated_df['CropCode'] = self.crop_id
            repeated_df['Year'] = 1

            #save crop managment
            self.__crop_management_df = repeated_df[['Location','Scenario','ID','ActualYear','CropCode',
                    'Year','PlantingDay','PlantingMon','HarvestDay','HarvestMon',
                    'HarvestEfficiency','HarvestType','HarvestIndexOverride','CNOP',
                    'StoverFraction','IsGrain','PRCOP']]

        return self.__crop_management_df
    
    @property
    def fertilizer_management_df(self)->pd.DataFrame:
        if self.__fertilizer_management_df  is None:
            default_fertilizer_management_df = self.__get_default_setup_df("default_fertilizer_management.csv")            
            
            repeated_df = default_fertilizer_management_df.loc[default_fertilizer_management_df.index.repeat(len(self.locations))].reset_index(drop=True)
            repeated_df["Scenario"] = self.scenario
            repeated_df["Location"] = np.sort(np.tile(self.locations, len(default_fertilizer_management_df)))
            repeated_df['Year'] = 1

            #save fertilizer managment
            self.__fertilizer_management_df = repeated_df[['Scenario','Location','Year','FerMon','FerDay',
                                                            'FerType','FerRate','FerSurface']]

        return self.__fertilizer_management_df
    
    @property
    def tillage_management_df(self)->pd.DataFrame:
        if self.__tillage_management_df  is None:
            default_tillage_management_df = self.__get_default_setup_df("default_tillage_management.csv")            
            
            repeated_df = default_tillage_management_df.loc[default_tillage_management_df.index.repeat(len(self.locations))].reset_index(drop=True)
            repeated_df["Scenario"] = self.scenario
            repeated_df["Location"] = np.sort(np.tile(self.locations, len(default_tillage_management_df)))
            repeated_df['Year'] = 1

            #save fertilizer managment
            self.default_tillage_management_df = repeated_df[['Scenario','Location','Year','TillMon','TillDay','TillCode']]

        return self.default_tillage_management_df
    