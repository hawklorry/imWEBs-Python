from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from .reach_parameter import ReachParameter
from .field_info import FieldInfo
from .farm_info import FarmInfo
from .subbasin_info import SubbasinInfo
from .field_subbasin import FieldSubbasin
from .field_farm import FieldFarm
from .farm_subbasin import FarmSubbasin
from ..database_base import DatabaseBase
from .bmp_table import BMPTable
from ...raster_extension import RasterExtension
from whitebox_workflows import WbEnvironment, Raster
from io import StringIO
import pandas as pd
import math

class reach_width_depth_parameter:
    def __init__(self, design_storm, parameter_A, parameter_B):
        self.A = parameter_A
        self.B = parameter_B
        self.design_storm = design_storm
        

class BMPDatabase(DatabaseBase):
    COL_NAME_AREA_HA = "Area_Ha"

    def __init__(self, database_file):
        super().__init__(database_file)
        self.__load()
        self.wbe = WbEnvironment()

    def __load(self):    
        self.reach_parameter = {}

        # Session = sessionmaker(bind=self.engine)
        # with Session() as session:
        #     select_stmt = select(ReachParameter)
        #     for row in session.scalars(select_stmt):
        #         self.reach_parameter[row.reach_id] = row

    def get_reach_parameter(self, reach_id, parameter_name):
        return getattr(self.reach_parameter[reach_id], parameter_name)
    
    def populate_database(self, subbasin_raster:Raster, 
                          field_raster:Raster, 
                          farm_raster:Raster, 
                          flow_acc_raster:Raster, 
                          potential_runoff_coefficient_raster:Raster, 
                          depression_storage_capacity_raster:Raster, 
                          cn2_raster:Raster):
        """
        create all the parameter tables in bmp database
        """
        
        #remove the tables we want to update and then create them again
        BMPTable.metadata.drop_all(self.engine)
        BMPTable.metadata.create_all(self.engine)

        print("creating field_info ...")
        field_area_df = RasterExtension.get_category_area_ha_dataframe(field_raster, BMPDatabase.COL_NAME_AREA_HA)
        field_area_df.to_sql(FieldInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        field_area_df.columns = ["FieldArea"]

        print("creating farm_info ...")
        farm_area_df = RasterExtension.get_category_area_ha_dataframe(farm_raster, BMPDatabase.COL_NAME_AREA_HA)
        farm_area_df.to_sql(FarmInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        farm_area_df.columns = ["FarmArea"]

        print("creating subbasin_info ...")
        subbasin_area_df = self.__create_subbasin_info(subbasin_raster, flow_acc_raster, potential_runoff_coefficient_raster, depression_storage_capacity_raster, cn2_raster)
        subbasin_area_df.to_sql(SubbasinInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        subbasin_area_df = subbasin_area_df[BMPDatabase.COL_NAME_AREA_HA].to_frame()
        subbasin_area_df.columns = ["SubbasinArea"]

        print("creating field_subbasin ...")
        self.__create_overlay(field_raster, subbasin_raster, "Field", "Subbasin", field_area_df, subbasin_area_df, FieldSubbasin.__tablename__)

        print("creating farm_subbasin ...")
        self.__create_overlay(farm_raster, subbasin_raster, "Farm", "Subbasin", farm_area_df, subbasin_area_df, FarmSubbasin.__tablename__)

        print("creating field_farm ...")
        self.__create_overlay(field_raster, farm_raster, "Field", "Farm", field_area_df, farm_area_df, FieldFarm.__tablename__)
 
    def __create_subbasin_info(self, 
                                subbasin_raster:Raster,
                                flow_acc_raster:Raster, 
                                potential_runoff_coefficient_raster:Raster, 
                                depression_storage_capacity_raster:Raster, 
                                cn2_raster:Raster):
        
        id_area_df = RasterExtension.get_category_area_ha_dataframe(subbasin_raster, BMPDatabase.COL_NAME_AREA_HA)
        id_flow_acc_max_df = RasterExtension.get_zonal_statistics(flow_acc_raster, subbasin_raster, "max", "FlowAcc_Max")
        id_prc_avg_df = RasterExtension.get_zonal_statistics(potential_runoff_coefficient_raster, subbasin_raster, "mean", "PRC_Avg")
        id_dsc_avg_df = RasterExtension.get_zonal_statistics(depression_storage_capacity_raster, subbasin_raster,"mean", "DSC_Avg")
        id_cn2_df = RasterExtension.get_zonal_statistics(cn2_raster, subbasin_raster,"mean", "CN2_Avg")
        
        #merge all info
        mergered_df = id_area_df.merge(id_flow_acc_max_df, left_index=True, right_index=True, how="inner")
        mergered_df = mergered_df.merge(id_prc_avg_df, left_index=True, right_index=True, how="inner")
        mergered_df = mergered_df.merge(id_dsc_avg_df, left_index=True, right_index=True, how="inner")
        mergered_df = mergered_df.merge(id_cn2_df, left_index=True, right_index=True, how="inner")

        return mergered_df

    def __create_overlay(self, spatial1_ras:Raster, spatial2_ras:Raster, name1:str, name2:str, raster1_area_df:pd.DataFrame, raster2_area_df:pd.DataFrame, table_name:str):
        overlay_area_df = self.__get_overlay_area(spatial1_ras, spatial2_ras, name1, name2)
        
        merged_df = overlay_area_df.merge(raster1_area_df, left_on= name1, right_index=True, how="left")
        merged_df = merged_df.merge(raster2_area_df, left_on= name2, right_index=True, how="left")

        #calculate the ratio
        merged_df["ID"] = merged_df.index + 1
        merged_df[f"To{name1}"] = merged_df[BMPDatabase.COL_NAME_AREA_HA] / merged_df[f"{name1}Area"]
        merged_df[f"To{name2}"] = merged_df[BMPDatabase.COL_NAME_AREA_HA] / merged_df[f"{name2}Area"]

        merged_df = merged_df[["ID", name1, name2, BMPDatabase.COL_NAME_AREA_HA, f"To{name1}", f"To{name2}"]]        
        merged_df.to_sql(table_name, con = self.engine, if_exists='append',index=False)
    
    def __get_overlay_area(self, spatial1_ras:Raster, spatial2_ras:Raster, name1:str, name2:str)->pd.DataFrame:
        #find max id from raster1        
        raster1_max = int(math.pow(10, int(math.log10(spatial1_ras.configs.maximum)) + 2))

        #make a new raster with a unique id combining both raster 1 and raster 2
        merged_raster = spatial1_ras + spatial2_ras * raster1_max
        df = RasterExtension.get_category_area_ha_dataframe(merged_raster,BMPDatabase.COL_NAME_AREA_HA)
        df[name1] = df.index % raster1_max
        df[name2] = (df.index - df[name1]) / raster1_max

        return df
    
    