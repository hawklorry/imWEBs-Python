from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select,insert
from whitebox_workflows import Vector
from ...vector_extension import VectorExtension
from .reach import Reach
from .reach_parameter import ReachParameter
from .field_info import FieldInfo
from .farm_info import FarmInfo
from .subbasin_info import SubbasinInfo
from .field_subbasin import FieldSubbasin
from .field_farm import FieldFarm
from .farm_subbasin import FarmSubbasin
from .subbasin_multiplier import SubbasinMultiplier
from ...delineation.structure import Structure
from ...names import Names
from ...bmp.bmp_areal_manure_storage import ArealBMPManureStorage
from ...bmp.bmp_reach_manure_catch_basin import ReachBMPManureCatchBasin
from ...bmp.bmp_reach_reservoir import ReachBMPReservoir
from ...bmp.bmp_type import BMPType
from ...bmp.bmp_reach import ReachBMP
from ...bmp.bmp import BMP
from ...bmp.bmp_structure_dugout import StructureBMPDugout
from ...bmp.bmp_structure_wascob import StructureBMPWascob
from ...bmp.bmp_offsite_wintering import BMPOffsiteWintering
from ...bmp.crop_rotation.crop_rotation import CropRotation
from .bmp_01_point_source import PointSource
from .bmp_02_flow_diversion import FlowDiversion
from .bmp_03_reservoir import Reservoir
# from .bmp_05_riparian_buffer import RiparianBuffer
# from .bmp_06_grass_waterway import GrassWaterWay
# from .bmp_07_vegetation_filter_strip import FilterStrip
from .bmp_09_isolated_wetland import Wetland
# from .bmp_12_crop_management import CropManagement, CropParameter
# from .bmp_14_tillage_management import TillageManagement, TillageParameter
# from .bmp_15_fertilizer_management import FertlizerManagement, FertilizerParameter
# from .bmp_16_grazing_management import GrazingManagement
# from .bmp_18_irrigation_management import irrigation_management, irrigation_parameter
# from .bmp_21_manure_incorporation_within_48h import ManureIncorporationWithin48hManagemet
# from .bmp_22_manure_application_setback import ManureApplicationSetbackManagement
# from .bmp_23_no_application_on_snow import ManureNoApplicaitonOnSnowManagement
# from .bmp_24_spring_application_rather_than_fall_application import ManureSpringApplicationRatherThanFallApplicationManagement
# from .bmp_25_applicaiton_based_on_soil_nitrogen_limit import ManureApplicationBasedOnSoliNitrogenLimitManagement
# from .bmp_26_applicaiton_based_on_soil_phosphorous_limit import ManureApplicationBasedOnPhosphorousLimitManagement
from .bmp_27_manure_storage import ManureStorageParameter
from .bmp_28_manure_catch_basin import ManureCatchBasinParameter
from .bmp_29_manure_feedlot import ManureFeedlot
# from .bmp_30_marginal_crop_management import MarginalCropManagement
# from .bmp_31_marginal_fertilizer_management import MarginalFertilizerManagement
# from .bmp_32_marginal_tillage_management import MarginalTillageManagement
# from .bmp_33_wintering_site_management import WinteringSiteManagement, WinteringSiteParameter
# from .bmp_34_pasture_crop_management import PastureCropManagement
# from .bmp_35_pasture_fertilizer_management import PastureFertilizerManagement
# from .bmp_36_pasture_tillage_management import Pasture_tillage_management
# from .bmp_37_pasture_grazing_management import PastureGrazingManagement, PastureGrazingParameter
# from .bmp_38_dugout import DugoutParameter
from .bmp_39_offsite_watering import OffsiteWateringParameter
from .bmp_40_managed_access_including_fencing import ManagedAccessIncludingFencingParameter
from .bmp_41_wascob import Wascob
#from .bmp_42_water_use import 


from ..database_base import DatabaseBase, logger
from .bmp_table import BMPTable
from ...raster_extension import RasterExtension
from whitebox_workflows import WbEnvironment, Raster
import pandas as pd
import math
import numpy as np
from ...outputs import Outputs

      

class BMPDatabase(DatabaseBase):
    default_tables = [Names.bmp_table_name_bmp_index,
                      Names.bmp_table_name_crop_parameter,
                      Names.bmp_table_name_crop_remove_parameter,
                      Names.bmp_table_name_fertilizer_parameter,
                      Names.bmp_table_name_tillage_parameter,
                      Names.bmp_table_name_livestock_parameter,                      
                      Names.bmp_table_name_ls_parameter]

    COL_NAME_AREA_HA = "Area_Ha"

    def __init__(self, database_file):
        super().__init__(database_file)
        self.wbe = WbEnvironment()             

    def populate_database(self, outputs:Outputs):
        """
        create all the parameter tables in bmp database
        """        

        #remove the tables we want to update and then create them again
        logger.info("Creating table structure in bmp database ...")
        BMPTable.metadata.drop_all(self.engine)
        BMPTable.metadata.create_all(self.engine)

        #default tables
        logger.info("Loading default tables to bmp database ...")
        for table in BMPDatabase.default_tables:
            logger.info(table)
            self.populate_defaults(table) 

        logger.info("Creating management_unit_info ...")
        field_area_df = RasterExtension.get_category_area_ha_dataframe(outputs.unit_management_raster, BMPDatabase.COL_NAME_AREA_HA)
        field_area_df.to_sql(Names.bmp_table_name_management_unit_info, con = self.engine, if_exists='replace',index=True)

        logger.info("Creating field_info ...")
        field_area_df = RasterExtension.get_category_area_ha_dataframe(outputs.field_raster, BMPDatabase.COL_NAME_AREA_HA)
        field_area_df.to_sql(Names.bmp_table_name_field_info, con = self.engine, if_exists='replace',index=True)
        field_area_df.columns = ["FieldArea"]

        logger.info("Creating farm_info ...")
        farm_area_df = RasterExtension.get_category_area_ha_dataframe(outputs.farm_raster, BMPDatabase.COL_NAME_AREA_HA)
        farm_area_df.to_sql(Names.bmp_table_name_farm_info, con = self.engine, if_exists='replace',index=True)
        farm_area_df.columns = ["FarmArea"]

        logger.info("Creating subbasin_info ...")
        subbasin_area_df = self.__create_subbasin_info(outputs.subbasin_raster, 
                                                       outputs.flow_acc_raster, 
                                                       outputs.potential_ruoff_coefficient_raster, 
                                                       outputs.depression_storage_capacity_raster, 
                                                       outputs.cn2_raster)
        subbasin_area_df.to_sql(Names.bmp_table_name_subbasin_info, con = self.engine, if_exists='replace',index=True)
        subbasin_ids = subbasin_area_df.index.to_list()

        subbasin_area_df = subbasin_area_df[BMPDatabase.COL_NAME_AREA_HA].to_frame()
        subbasin_area_df.columns = ["SubbasinArea"]

        logger.info("Creating field_subbasin ...")
        self.__create_overlay(outputs.field_raster, outputs.subbasin_raster, 
                              "Field", "Subbasin", field_area_df, subbasin_area_df, Names.bmp_table_name_field_subbasin)

        logger.info("Creating farm_subbasin ...")
        self.__create_overlay(outputs.farm_raster, outputs.subbasin_raster, 
                              "Farm", "Subbasin", farm_area_df, subbasin_area_df, Names.bmp_table_name_farm_subbasin)

        logger.info("Creating field_farm ...")
        self.__create_overlay(outputs.field_raster, outputs.farm_raster, 
                              "Field", "Farm", field_area_df, farm_area_df, Names.bmp_table_name_field_farm) 
        
        self.__create_subbasin_multiplier(subbasin_ids)

        #bmps
        reach_bmps = {}
        reach_bmps[BMPType.BMP_TYPE_RESERVOIR] = self.__create_bmp_reservoir(outputs)
        for type, struc in outputs.structures.items():            
            id_subbasins = self.__create_bmp_structure(type, struc, outputs)
            if type == "wetland":
                reach_bmps[BMPType.BMP_TYPE_WETLAND] = id_subbasins
        self.__create_bmp_manure_storage(outputs)   
        reach_bmps[BMPType.BMP_TYPE_MANURE_CATCHBASIN] = self.__create_bmp_manure_catchbasin(outputs) 
        self.__create_bmp_riparian_buffer(outputs)
        self.__create_bmp_offsite_wintering(outputs)


        #create reach_bmp table
        #all reach bmps should be added before this
        self.__create_reach_parameter(outputs)
        self.__create_bmp_reach_bmp(subbasin_ids, reach_bmps)

        #create bmp_scenarios table
        self.__create_bmp_scenarios(outputs)

        #just force to generate the reach vector, change it later
        reach = outputs.reach_vector

    def update_crop_rotation_AAFC_crop_inventory(self, crop_inventory_folder:str, first_year:int, last_year:int, outputs:Outputs):        
        logger.info("Updating crop rotation based on AAFC Crop Inventory ... ")

        rotation = CropRotation(outputs.field_clipped_vector, outputs.subbasin_raster,crop_inventory_folder, first_year, last_year)
        
        logger.info("Crop Management ... ")
        self.save_table(Names.bmp_table_name_crop_management, rotation.crop_management_df)

        logger.info("Fertilizer Management ... ")
        self.save_table(Names.bmp_table_name_fertilizer_management, rotation.fertilizer_management_df)

        logger.info("Tillage Management ... ")
        self.save_table(Names.bmp_table_name_tillage_management, rotation.tillage_management_df)

        logger.info("Grazing Management ... ")
        self.save_table(Names.bmp_table_name_grazing_management, rotation.grazing_management_df)

        logger.info("Grazing reach deposit ... ")
        self.create_grazing_reach_deposit(first_year)

        logger.info("Updating scenarios ...")
        self.__create_bmp_scenarios(outputs, True)

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
        merged_df["ID"] = merged_df.index
        merged_df[f"To{name1}"] = merged_df[BMPDatabase.COL_NAME_AREA_HA] / merged_df[f"{name1}Area"]
        merged_df[f"To{name2}"] = merged_df[BMPDatabase.COL_NAME_AREA_HA] / merged_df[f"{name2}Area"]

        merged_df = merged_df[["ID", name1, name2, BMPDatabase.COL_NAME_AREA_HA, f"To{name1}", f"To{name2}"]]     
        self.save_table(table_name, merged_df)   
    
    def __get_overlay_area(self, spatial1_ras:Raster, spatial2_ras:Raster, name1:str, name2:str)->pd.DataFrame:
        merged_raster, raster1_max = RasterExtension.get_overlay_raster(spatial1_ras, spatial2_ras)
        df = RasterExtension.get_category_area_ha_dataframe(merged_raster,BMPDatabase.COL_NAME_AREA_HA)
        df[name1] = df.index % raster1_max
        df[name2] = (df.index - df[name1]) / raster1_max

        return df
    
    def create_grazing_reach_deposit(self, start_year:int):
        """
        Create GRAMG_ReachDeposit table based on GRAMG_management, Field_Info, Livestock_parameter and Fertilizer_parameter.

        It pre-calculate the manure deposit at each reach on each day as a way to speed the engine calculation. Could and should be done in the engine. 

        The table name GRAMG_ReachDeposit and GRAMG_management is fixed in the engine so it couldn't be renamed, which should be avoided. 

        This replace the GenerateGrazingReachDeposit function in Whitebox-based interface. 
        
        """
        
        grazing_management_df = self.read_table("GRAMG_management")
        if grazing_management_df is None:
            return 

        field_info_df = self.read_table(Names.bmp_table_name_field_info)
        livestock_parameter = self.read_table(Names.bmp_table_name_livestock_parameter)
        fertilizer_parameter = self.read_table(Names.bmp_table_name_fertilizer_parameter)

        #inner join grazing_management, field_info and livestock_parameter
        reach_deposit_df = grazing_management_df[grazing_management_df["Source"] == 1]
        reach_deposit_df = reach_deposit_df[reach_deposit_df["Access"] != 2]
        reach_deposit_df = reach_deposit_df.merge(field_info_df, left_on="Location", right_on= "id", how="inner")
        reach_deposit_df = reach_deposit_df.merge(livestock_parameter, left_on="Ani_ID", right_on="ID", how="inner")
        reach_deposit_df = reach_deposit_df.merge(fertilizer_parameter, left_on="Man_ID", right_on="IFNUM", how="inner")

        #calcualte manure and drinkwater
        reach_deposit_df["Manure"] = reach_deposit_df["GR_Density"] * reach_deposit_df["Area_Ha"] * reach_deposit_df["Ani_Weight"] * reach_deposit_df["Ani_adult"] / 100 / 1000 * reach_deposit_df["Man_Day"] * reach_deposit_df["DayFra"] * reach_deposit_df["Drinking_time"]
        reach_deposit_df["DrinkWater"] = reach_deposit_df["GR_Density"] * reach_deposit_df["Area_Ha"] * reach_deposit_df["Ani_Weight"] * reach_deposit_df["Ani_adult"] / 100 * reach_deposit_df["Water_Drink"] / 100 / 1000 

        #further calculation and rename
        reach_deposit_df["Year"] = reach_deposit_df["Year"] + start_year - 1
        reach_deposit_df["Month"] = reach_deposit_df["GraMon"]
        reach_deposit_df["Day"] = reach_deposit_df["GraDay"]
        reach_deposit_df["StartDate"] = pd.to_datetime(reach_deposit_df[["Year","Month","Day"]])
        reach_deposit_df["ReachId"] = reach_deposit_df["SourceID"]
        reach_deposit_df["TSS"] = reach_deposit_df["Man_TSS_Fra"] / 100 * reach_deposit_df["Manure"]
        reach_deposit_df["NO3"] = reach_deposit_df["FMINN"]  * reach_deposit_df["Manure"]
        reach_deposit_df["NH4"] = 0
        reach_deposit_df["OrgN"] = reach_deposit_df["FORGN"] * reach_deposit_df["Manure"]
        reach_deposit_df["SolP"] = reach_deposit_df["FMINP"] * reach_deposit_df["Manure"]
        reach_deposit_df["OrgP"] = reach_deposit_df["FORGP"] * reach_deposit_df["Manure"]

        #just keep the useful columns
        reach_deposit_df = reach_deposit_df[["ReachId","StartDate","Days","Manure","TSS","NO3","NH4","OrgN","SolP","OrgP","DrinkWater","BankK_Change"]]

        #repeat per the days column
        expanded_reach_deposit_dfs = []
        for index in range(len(reach_deposit_df)):
            #repeat the records based on the number of days and set the date
            repeated_df = pd.DataFrame(np.repeat(reach_deposit_df.iloc[[index]].values,reach_deposit_df.iloc[index].Days,axis=0),columns=reach_deposit_df.columns).reset_index()
            temp = repeated_df["index"].apply(lambda x: pd.Timedelta(x, unit='D'))
            repeated_df["Date"] = repeated_df["StartDate"] + temp
            expanded_reach_deposit_dfs.append(repeated_df)

        #concat
        reach_deposit_df = pd.concat(expanded_reach_deposit_dfs)

        #aggregate for each and date
        reach_deposit_df = pd.pivot_table(reach_deposit_df, 
                        index = ["ReachId","Date"], 
                        values =["Manure","TSS","NO3","NH4","OrgN","SolP","OrgP","DrinkWater","BankK_Change"],
                        aggfunc={"Manure":"sum",
                                "TSS":"sum",
                                "NO3":"sum",
                                "NH4":"sum",
                                "OrgN":"sum",
                                "SolP":"sum",
                                "OrgP":"sum",
                                "DrinkWater":"sum",
                                "BankK_Change":"min"})

        reach_deposit_df.reset_index(inplace=True)

        #get year, month and day
        reach_deposit_df["Year"] = reach_deposit_df["Date"].dt.year - start_year + 1
        reach_deposit_df["Month"] = reach_deposit_df["Date"].dt.month
        reach_deposit_df["Day"] = reach_deposit_df["Date"].dt.day

        #get required columns
        reach_deposit_df = reach_deposit_df[["ReachId","Year","Month","Day","Manure","TSS","NO3","NH4","OrgN","SolP","OrgP","DrinkWater","BankK_Change"]]

        #save to database
        self.save_table("GRAMG_ReachDeposit",reach_deposit_df)


#region BMPs

    def __create_subbasin_multiplier(self, subbasin_ids:list)->None:
        """populate default subbasin-muliplier"""
        logger.info("Creating subbasin_multiplier ... ")
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            session.add_all([SubbasinMultiplier(id) for id in subbasin_ids])
            session.commit()

    def __create_bmp_structure(self, structure_type:str, structure:Structure,outputs:Outputs)->dict:
        """populate default structure parameter table""" 
        logger.info(f"Creating {structure_type} parameter table ... ")      

        if structure_type == "wetland" or structure_type == "feedlot":
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                if structure_type == "wetland":
                    session.add_all([Wetland(struc_attribute) for struc_attribute in structure.attributes.values()])
                elif structure_type == "feedlot":
                    session.add_all([ManureFeedlot(struc_attribute) for struc_attribute in structure.attributes.values()])
                session.commit()
        else:
            #we couldn't create dugout and wascob parameter table with ORM as the primary key is not defined. Use pandas dataframe instead
            if structure_type == "dugout":
                self.__create_bmp_dugout(self,outputs,structure)
            elif structure_type == "wascob":
                self.__create_bmp_wascob(self,outputs,structure)
        

        id_subbasins = {}
        for id, attribute in structure.attributes.items():
            id_subbasins[id] = attribute.subbasin
        return id_subbasins

    def __create_bmp_riparian_buffer(self, outputs:Outputs):
        df = outputs.riparian_buffer_parameter_df
        if df is not None:
            self.save_table(Names.bmp_table_name_riparian_buffer, df)

    def __create_bmp_dugout(self, outputs:Outputs, dugout_structure:Structure):
        dugout = StructureBMPDugout(outputs.inputs.dugout_boundary_vector, outputs.subbasin_raster, dugout_structure)
        self.save_table(Names.bmp_table_name_dugout, dugout.dugout_df)

    def __create_bmp_wascob(self, outputs:Outputs, wascob_structure:Structure):
        wascob = StructureBMPWascob(outputs.inputs.dugout_boundary_vector, outputs.subbasin_raster, wascob_structure)
        self.save_table(Names.bmp_table_name_dugout, wascob.wascob_df)

    def __create_bmp_manure_storage(self,outputs:Outputs):
        """populate default manure storage tables"""
        if outputs.inputs.manure_storage_boundary_vector is None:
            return
        
        logger.info("Creating manure storage parameter table ... ")
        storage = ArealBMPManureStorage(outputs.inputs.manure_storage_boundary_vector,
                                outputs.flow_direction_raster,
                                outputs.subbasin_raster,
                                outputs.reach_raster,
                                outputs.dem_clipped_raster)
        
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            session.add_all(storage.manure_storage_parameters)
            session.commit()  

    def __create_bmp_reservoir(self, outputs:Outputs)->dict:
        """populate default reservoir parameter table"""
        if outputs.inputs.reservoir_vector is None:
            return {}
        
        logger.info("Creating reservoir parameter table ... ")
        reservoir = ReachBMPReservoir(outputs.inputs.reservoir_vector, outputs.subbasin_raster)
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            session.add_all(reservoir.reservoirs)
            session.commit()  

        return reservoir.subbasins

    def __create_bmp_manure_catchbasin(self, outputs:Outputs)->dict:
        if outputs.inputs.catchbasin_vector is None:
            return {}
        
        logger.info("Creating manure catch basin parameter table ... ")
        catchbasin = ReachBMPManureCatchBasin(outputs.inputs.catchbasin_vector,
                                outputs.subbasin_raster,
                                outputs.reach_parameter_df)
        
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            session.add_all(catchbasin.manure_catch_basin_parameters)
            session.commit()         

        return catchbasin.subbasins
    
    def __create_bmp_offsite_wintering(self, outputs:Outputs):
        if outputs.inputs.offsite_watering_vector is None:
            return
        
        logger.info("Creating offsite wintering parameter table ... ")
        bmp = BMPOffsiteWintering(outputs.inputs.offsite_watering_vector, outputs.subbasin_raster)

        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            session.add_all(bmp.offsite_wintering_parameters)
            session.commit()      

    def __create_reach_parameter(self, outputs:Outputs):
        """crete reach parameters"""
        logger.info("Creating reach_parameter table ... ")
        self.save_table(Names.bmp_table_name_reach_parameter, outputs.reach_parameter_df)
    
    def __create_bmp_reach_bmp(self, subbasin_ids:list, reach_bmps:dict):
        """create reach_bmp table"""

        logger.info("Creating reach_bmp table ... ")
        df = ReachBMP.create_reach_bmp_df(subbasin_ids, reach_bmps)
        self.save_table(Names.bmp_table_name_reach_bmp, df)

    def __create_bmp_scenarios(self, outputs:Outputs, include_crop_rotation:bool = False):
        """create bmp scenarios table"""
        
        logger.info("Creating bmp_secenarios table ... ")

        bmp_types = outputs.inputs.bmp_types
        if include_crop_rotation:
            bmp_types.append(BMPType.BMP_TYPE_CROP)
            bmp_types.append(BMPType.BMP_TYPE_FERTILIZER)
            bmp_types.append(BMPType.BMP_TYPE_TILLAGE)
            bmp_types.append(BMPType.BMP_TYPE_GRAZING)

        df = BMP.generate_bmp_scenarios_df(bmp_types)
        self.save_table(Names.bmp_table_name_scenarios, df)

#endregion