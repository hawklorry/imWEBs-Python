import pandas as pd
import os
import numpy as np
import random
from ..bmp import BMP
from ..bmp_type import DefaultScenarioId
from whitebox_workflows import Vector, Raster
from ...raster_extension import RasterExtension
from ...vector_extension import VectorExtension
from ...folder_base import FolderBase

from ...database.bmp.bmp_12_crop_management import CropManagement
from ...database.bmp.bmp_15_fertilizer_management import FertlizerManagement
from ...database.bmp.bmp_14_tillage_management import TillageManagement
from ...database.bmp.bmp_16_grazing_management import GrazingManagement

import logging
logger = logging.getLogger(__name__)

class CropRotation(FolderBase):
    flag_not_proceed = "Not proceed"    
    col_location = "Location"
    col_year = "Year"
    col_original_crop_id = "Original ID"
    col_imwebs_crop_id = "IMWEBs ID"
    col_crop_code = "CropCode"

    #create random date between first and last day
    col_planting_date = ('PlantingMon', 'PlantingDay')
    col_harvest_date = ('HarvestMon', 'HarvestDay')
    col_fertilizer_date = ('FerMon', 'FerDay')
    col_tillage_date = ('TillMon', 'TillDay')
    value_planting_date = -1000
    value_harvest_date = -100

    def __init__(self, 
                 management_unit_vector:Vector,
                 subbasin_raster: Raster,
                 crop_inventory_raster_folder:str, 
                 first_year:int, 
                 last_year:int,
                 scenario:int = DefaultScenarioId):
        super().__init__(crop_inventory_raster_folder)
        self.management_unit_vector = management_unit_vector
        self.subbasin_raster = subbasin_raster
        self.first_year = first_year
        self.last_year = last_year
        self.scenario = scenario

        exist, self.id_field_name = VectorExtension.check_id(self.management_unit_vector)
        if not exist:
            raise ValueError(f"There is no id column in {self.management_unit_vector.file_name}.")

        self.__dominant_crop_df = None
        self.__default_setup_dfs = {}
        self.__crop_management_df = None
        self.__fertilizer_management_df = None
        self.__tillage_management_df = None
        self.__grazing_management_df = None

    def __get_default_file_path(self, file_name)->str:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        if not os.path.exists(file_path):
            raise ValueError(f"{file_path} doesn't exist. Please check the crop rotation folder.")
        
        return file_path

    def __get_default_setup_df(self, file_name:str)->pd.DataFrame:
        if file_name not in self.__default_setup_dfs:      
            #search in the crop inventory folder first
            setup_file_path = self.get_file_path(file_name)
            if not os.path.exists(setup_file_path):
                setup_file_path = self.__get_default_file_path(file_name)

            df = pd.read_csv(setup_file_path)  
            if "crop-lookup" in file_name:
                df = df[df[self.col_imwebs_crop_id]!= self.flag_not_proceed]
                df[self.col_imwebs_crop_id] = df[self.col_imwebs_crop_id].astype(int)
            self.__default_setup_dfs[file_name] = df

        return self.__default_setup_dfs[file_name]

    def __get_crop_code_lookup_df(self, year):
        try:
            return self.__get_default_setup_df("crop-lookup.csv")
        except:
            return self.__get_default_setup_df("crop-lookup-before-2010.csv") if year <=2010 else self.__get_default_setup_df("crop-lookup-after-2010.csv")

    @property
    def domimant_crop_df(self)->pd.DataFrame:
        """domminant crop dataframe for each year"""
        if self.__dominant_crop_df is None:
            field_crop_df_list = []
            for year in range(self.first_year, self.last_year + 1):
                file_name = f"{year}.tif"
                logger.info(file_name)
                crop_raster = self.get_raster(file_name)
                if crop_raster is None:
                    raise ValueError(f"Couldn't find {self.get_file_path(file_name)}.")

                #clip the crop raster to the field vector
                #logger.info("clip ...")
                clipped_crop_raster = self.wbe.clip_raster_to_polygon(raster = crop_raster, polygons = self.management_unit_vector)

                #covert the field vector to raster  
                #logger.info("to raster ...")            
                field_raster = self.wbe.vector_polygons_to_raster(
                                                        input=self.management_unit_vector, 
                                                        base_raster = clipped_crop_raster, 
                                                        field_name = self.id_field_name)
                
                #get dominant crop for each field
                #logger.info("get majority count ...")
                field_dominant_crop = RasterExtension.get_majority_count(clipped_crop_raster, field_raster)

                #create dataframe and save the original crop id to Original ID column
                df = pd.DataFrame.from_dict(field_dominant_crop, orient = 'index', columns = [self.col_original_crop_id])
                df.index.name = self.col_location
                df = df.sort_index()
                df = df.reset_index()
                df['ActualYear'] = year
                df['Year'] = year - self.first_year + 1

                #map to imwebs crop id
                #read crop lookup csv file and dicard not proccessed codes
                df_crop_code_lookup = self.__get_crop_code_lookup_df(year)               

                #join original id and imweb code
                df_field_crop_imwebs = df.merge(df_crop_code_lookup, how = 'inner', on = self.col_original_crop_id)
                df_field_crop_imwebs[self.col_crop_code] = df_field_crop_imwebs[self.col_imwebs_crop_id]

                #add to the list
                field_crop_df_list.append(df_field_crop_imwebs)

            self.__dominant_crop_df = pd.concat(field_crop_df_list, ignore_index=True)
            self.__dominant_crop_df ['Scenario'] = self.scenario
        
        return self.__dominant_crop_df

    @property
    def crop_management_df(self)->pd.DataFrame:
        if self.__crop_management_df  is None:
            #crop management
            df_crop_management_lookup = self.__get_default_setup_df("crop-management.csv")
            df_crop = self.domimant_crop_df.merge(df_crop_management_lookup, how = 'inner', on = self.col_crop_code)

            #add planting and harvest month and day column
            for col in self.col_planting_date + self.col_harvest_date:
                df_crop[col] = -1
                
            #add ID column
            df_crop['ID'] = df_crop['Location']

            #populate the columns
            for index in df_crop.index:    
                #planting dates
                CropRotation.populate_random_date(df_crop, index, self.col_planting_date[0], self.col_planting_date[1])
                
                #harvest dates
                CropRotation.populate_random_date(df_crop, index, self.col_harvest_date[0], self.col_harvest_date[1])

            for index in df_crop.index: 
                #change the planting date of crops that are planted in previous year
                CropRotation.move_winter_wheat_planting_day(df_crop, index)

            #Get the year. If previous year flag is 1, then previous year is used.
            df_crop['Year'] = np.where(df_crop['Pervious Year'] == 1, df_crop['Year'] - 1, df_crop['Year'])

            #if the year is zero, then it's winter wheat and we will use year 1 and set plant day to Jan 1st
            df_crop[self.col_planting_date[0]] = np.where(df_crop['Year'] == 0, 1, df_crop[self.col_planting_date[0]])
            df_crop[self.col_planting_date[1]] = np.where(df_crop['Year'] == 0, 1, df_crop[self.col_planting_date[1]])
            df_crop['Year'] = np.where(df_crop['Year'] == 0, 1, df_crop['Year'])
                
            #save crop managment
            self.__crop_management_df = df_crop[['Location','Scenario','ID','ActualYear','CropCode',
                    'Year','PlantingDay','PlantingMon','HarvestDay','HarvestMon',
                    'HarvestEfficiency','HarvestType','HarvestIndexOverride','CNOP',
                    'StoverFraction','IsGrain','PRCOP']]
            
        return self.__crop_management_df

    @property
    def fertilizer_management_df(self)->pd.DataFrame:
        if self.__fertilizer_management_df is None:
            df_fer_management_lookup = self.__get_default_setup_df("fertilizer-management.csv")
            df_fertilizer = self.crop_management_df.merge(df_fer_management_lookup, how = 'inner', on = self.col_crop_code)

            #add the columns
            for col in self.col_fertilizer_date:
                df_fertilizer[col] = -1

            #populate the columns
            for index in df_fertilizer.index:    
                #fertilizer dates
                CropRotation.populate_random_date(df_fertilizer, index, self.col_fertilizer_date[0], self.col_fertilizer_date[1])
                
            #save fertilizer managment
            self.__fertilizer_management_df = df_fertilizer[['Scenario','Location','Year','FerMon','FerDay',
                                                            'FerType','FerRate','FerSurface']]
        return self.__fertilizer_management_df

    @property
    def tillage_management_df(self)->pd.DataFrame:
        if self.__tillage_management_df is None:
               #-------------------------------------------------------------------------------------------------
            #tillage management   
            df_til_management_lookup = self.__get_default_setup_df("tillage-management.csv")
            df_tillage = self.crop_management_df.merge(df_til_management_lookup, how = 'inner', on = self.col_crop_code)
                
            #add the columns
            for col in self.col_tillage_date:
                df_tillage[col] = -1
                    
            #populate the columns
            for index in df_tillage.index:
                #tillage dates
                CropRotation.populate_random_date(df_tillage, index, self.col_tillage_date[0], self.col_tillage_date[1])
                
            #save tillage managment
            self.__tillage_management_df = df_tillage[['Scenario','Location','Year','TillMon','TillDay','TillCode']]

        return self.__tillage_management_df

    @property
    def grazing_management_df(self)->pd.DataFrame:
        if self.__grazing_management_df is None:
            df_grazaing_management_lookup = self.__get_default_setup_df("grazing-management.csv")
            df_grazing = self.domimant_crop_df.merge(df_grazaing_management_lookup, how = 'inner', on = self.col_crop_code)

            #get field to subbasin mapping
            id_subbasin_dict = BMP(self.management_unit_vector, self.subbasin_raster).subbasins
            df_field_subbasin_lookup = pd.DataFrame(list(id_subbasin_dict.items()),columns=["Location","SourceID"])
            df_grazing = df_grazing.merge(df_field_subbasin_lookup, how = 'inner', on = 'Location')

            #save grazing managment
            self.__grazing_management_df = df_grazing[['Scenario','Location','Year','GraMon','GraDay','Days',
            'Ani_ID','Ani_adult','GR_Density','DayFra','Source', 'SourceID','Dugout_ID','Access','Fencing','StreamAniPerc', 'Drinking_time','BankK_Change']]

        return self.__grazing_management_df

#region select random date

    @staticmethod
    def create_random_date(mon_first, day_first, mon_last, day_last):
        """create random planting month and day"""
        first_day = pd.Timestamp(year = 2000, month = mon_first, day = day_first)
        last_day = pd.Timestamp(year = 2000, month = mon_last, day = day_last)
        day_range = last_day - first_day
        ran = random.randint(0, day_range.days)
        ran_day = first_day + pd.Timedelta(f'{ran} days')
        return (ran_day.month, ran_day.day)

    @staticmethod
    def offset_days(mon, day, offset_days):
        d = pd.Timestamp(year = 2000, month = mon, day = day)
        d = d + pd.Timedelta(f'{offset_days} days')
        
        return (d.month, d.day)

    @staticmethod
    def populate_random_date(df, index, col_mon, col_day):
        """populate the random date for given index and mon/day column"""
        mon_first = df.loc[index, f'{col_mon}_First']
        day_first = df.loc[index, f'{col_day}_First']
        mon_last = df.loc[index, f'{col_mon}_Last']
        day_last = df.loc[index, f'{col_day}_Last']
        
        
        new_month_day = None
        if mon_first < 0 or day_first < 0 or mon_last < 0 or day_last < 0: 
            if CropRotation.__is_referencing_harvest_date(mon_first) or \
                CropRotation.__is_referencing_harvest_date(day_first) or \
                CropRotation.__is_referencing_harvest_date(mon_first) or \
                CropRotation.__is_referencing_harvest_date(day_first):
                #after harvest day
                days_after_harvest = CropRotation.__day_after_harvest(mon_first)
                new_month_day = CropRotation.offset_days(df.loc[index, CropRotation.col_harvest_date[0]], df.loc[index, CropRotation.col_harvest_date[1]], days_after_harvest)
            else:
                #around plating day
                days_related_to_planting = CropRotation.__day_related_to_planting(mon_first)
                new_month_day = CropRotation.offset_days(df.loc[index, CropRotation.col_planting_date[0]], df.loc[index, CropRotation.col_planting_date[1]], days_related_to_planting)
        else:    
            #random day
            new_month_day = CropRotation.create_random_date(mon_first, day_first, mon_last, day_last)    
            
            
        df.loc[index, col_mon] = new_month_day[0]
        df.loc[index, col_day] = new_month_day[1]

    @staticmethod
    def __is_referencing_harvest_date(mon_day:int)->bool:
        return mon_day < 0 and mon_day > CropRotation.value_harvest_date
    
    @staticmethod
    def __day_after_harvest(mon_day:int)->int:
        return mon_day - CropRotation.value_harvest_date
    
    @staticmethod
    def __is_referencing_planting_date(mon_day:int)->bool:
        return mon_day < CropRotation.value_harvest_date
    
    @staticmethod
    def __day_related_to_planting(mon_day:int)->int:
        return mon_day - CropRotation.value_planting_date

    @staticmethod
    def move_winter_wheat_planting_day(df, index):
        """
            make sure the planting day of winter wheat is after the harvest day of previous crop
            if not, set it to the harvest day of previous crop
        """
        #only apply to crop where the previous year flag is 1
        if df.loc[index, 'Pervious Year'] != 1:
            return
        #only apply to crop on the second years and after as the first year will be set to Jan 1st
        year = df.loc[index, 'Year']
        if year == 1:
            return
        #get crop of previous year
        location = df.loc[index, 'Location']
        previous_crop_df = df[(df['Year'] == year - 1) & (df['Location'] == location)]

        #return if previous crop doesn't exist
        if len(previous_crop_df.index) == 0:
            return

        #get harvest date
        harvest_mon = previous_crop_df.loc[previous_crop_df.index[0],CropRotation.col_harvest_date[0]]
        harvest_day = previous_crop_df.loc[previous_crop_df.index[0],CropRotation.col_harvest_date[1]]
        harvest_date = pd.Timestamp(year = 2000, month = harvest_mon, day = harvest_day)

        #get planting date
        planting_mon = df.loc[index,CropRotation.col_planting_date[0]]
        planting_day = df.loc[index,CropRotation.col_planting_date[1]]
        planting_date = pd.Timestamp(year = 2000, month = planting_mon, day = planting_day)

        #print(f"Location = {location}, Year = {year}, Planting = {planting_mon}-{planting_day}, Previous Harvest = {harvest_mon}-{harvest_day}")

        #check planting date
        if planting_date >= harvest_date:
            return

        #chang it to harvest date
        df.loc[index,CropRotation.col_planting_date[0]] = harvest_mon
        df.loc[index,CropRotation.col_planting_date[1]] = harvest_day

        #print(f"Changed, Planting = {df.loc[index,col_planting_date[0]]}-{df.loc[index,col_planting_date[1]]}")


#endregion

