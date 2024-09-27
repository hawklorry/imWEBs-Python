from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from .reach_parameter import ReachParameter
from .field_info import FieldInfo
from .farm_info import FarmInfo
from .subbasin_info import SubbasinInfo
from .field_subbasin import FieldSubbasin
from .field_farm import FieldFarm
from .farm_subbasin import FarmSubbasin
# from .bmp_01_point_source import PointSource
# from .bmp_02_flow_diversion import FlowDiversion
# from .bmp_03_reservoir import Reservoir
# from .bmp_05_riparian_buffer import RiparianBuffer
# from .bmp_06_grass_waterway import GrassWaterWay
# from .bmp_07_vegetation_filter_strip import FilterStrip
# from .bmp_09_isolated_wetland import Wetland
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
# from .bmp_27_manure_storage import ManureStorageCapacityAndDesignManagement, ManureStorageCapacityAndDesignParameter
# from .bmp_28_manure_catch_basin import ManureCatchBasinImpondmentParameter
# from .bmp_29_manure_feedlot import ManureFeedlotManagement, ManureFeedlotParameter
# from .bmp_30_marginal_crop_management import MarginalCropManagement
# from .bmp_31_marginal_fertilizer_management import MarginalFertilizerManagement
# from .bmp_32_marginal_tillage_management import MarginalTillageManagement
# from .bmp_33_wintering_site_management import WinteringSiteManagement, WinteringSiteParameter
# from .bmp_34_pasture_crop_management import PastureCropManagement
# from .bmp_35_pasture_fertilizer_management import PastureFertilizerManagement
# from .bmp_36_pasture_tillage_management import Pasture_tillage_management
# from .bmp_37_pasture_grazing_management import PastureGrazingManagement, PastureGrazingParameter
# from .bmp_38_dugout import DugoutParameter
# from .bmp_39_offsite_watering import OffsiteWateringParameter
# from .bmp_40_managed_access_including_fencing import ManagedAccessIncludingFencingParameter


from ..database_base import DatabaseBase, logger
from .bmp_table import BMPTable
from ...raster_extension import RasterExtension
from whitebox_workflows import WbEnvironment, Raster
from io import StringIO
import pandas as pd
import math
import numpy as np

class reach_width_depth_parameter:
    def __init__(self, design_storm, parameter_A, parameter_B):
        self.A = parameter_A
        self.B = parameter_B
        self.design_storm = design_storm
        

class BMPDatabase(DatabaseBase):
    default_tables = ["bmp_index",
                      "crop_parameter","fertilizer_parameter","tillage_parameter",
                      "manure_and_nutrient_parameter","livestock_parameter",
                      "crop_remove_parameter","LS_parameter"]

    COL_NAME_AREA_HA = "Area_Ha"

    def __init__(self, database_file):
        super().__init__(database_file)
        self.wbe = WbEnvironment()             

    # def get_reach_parameter(self, reach_id, parameter_name):
    #     return getattr(self.reach_parameter[reach_id], parameter_name)   

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
        logger.info("Creating table structure in bmp database ...")
        BMPTable.metadata.drop_all(self.engine)
        BMPTable.metadata.create_all(self.engine)

        #default tables
        logger.info("Loading default tables to bmp database ...")
        for table in BMPDatabase.default_tables:
            logger.info(table)
            self.populate_defaults(table) 

        logger.info("creating field_info ...")
        field_area_df = RasterExtension.get_category_area_ha_dataframe(field_raster, BMPDatabase.COL_NAME_AREA_HA)
        field_area_df.to_sql(FieldInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        field_area_df.columns = ["FieldArea"]

        logger.info("creating farm_info ...")
        farm_area_df = RasterExtension.get_category_area_ha_dataframe(farm_raster, BMPDatabase.COL_NAME_AREA_HA)
        farm_area_df.to_sql(FarmInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        farm_area_df.columns = ["FarmArea"]

        logger.info("creating subbasin_info ...")
        subbasin_area_df = self.__create_subbasin_info(subbasin_raster, flow_acc_raster, potential_runoff_coefficient_raster, depression_storage_capacity_raster, cn2_raster)
        subbasin_area_df.to_sql(SubbasinInfo.__tablename__, con = self.engine, if_exists='append',index=True)
        subbasin_area_df = subbasin_area_df[BMPDatabase.COL_NAME_AREA_HA].to_frame()
        subbasin_area_df.columns = ["SubbasinArea"]

        logger.info("creating field_subbasin ...")
        self.__create_overlay(field_raster, subbasin_raster, "Field", "Subbasin", field_area_df, subbasin_area_df, FieldSubbasin.__tablename__)

        logger.info("creating farm_subbasin ...")
        self.__create_overlay(farm_raster, subbasin_raster, "Farm", "Subbasin", farm_area_df, subbasin_area_df, FarmSubbasin.__tablename__)

        logger.info("creating field_farm ...")
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
    
    def __create_grazing_reach_deposit(self, start_year:int):
        """
        Create GRAMG_ReachDeposit table based on GRAMG_management, Field_Info, Livestock_parameter and Fertilizer_parameter.

        It pre-calculate the manure deposit at each reach on each day as a way to speed the engine calculation. Could and should be done in the engine. 

        The table name GRAMG_ReachDeposit and GRAMG_management is fixed in the engine so it couldn't be renamed, which should be avoided. 

        This replace the GenerateGrazingReachDeposit function in Whitebox-based interface. 
        
        """
        
        grazing_management_df = self.read_table("GRAMG_management")
        field_info_df = self.read_table("field_info")
        livestock_parameter = self.read_table("livestock_parameter")
        fertilizer_parameter = self.read_table("fertilizer_parameter")

        #inner join grazing_management, field_info and livestock_parameter
        reach_deposit_df = grazing_management_df[grazing_management_df["Source"] == 1]
        reach_deposit_df = reach_deposit_df[reach_deposit_df["Access"] != 2]
        reach_deposit_df = reach_deposit_df.merge(field_info_df, left_on="Location", right_index=True, how="inner")
        reach_deposit_df = reach_deposit_df.merge(livestock_parameter, left_on="Ani_ID", right_index=True, how="inner")
        reach_deposit_df = reach_deposit_df.merge(fertilizer_parameter, left_on="Man_ID", right_index=True, how="inner")

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

    def __create_riparian_buffer_distribution_paramter(self,
                                                       riparian_buffer_raster:Raster,
                                                       flow_dir_raster:Raster,
                                                       subbasin_raster:Raster,
                                                       slope_radius_raster:Raster,
                                                       soil_k_raster:Raster,
                                                       soil_porosity_raster:Raster,
                                                       landuse_rootdepth_raster:Raster,
                                                       width = 10):
        """
        create distribution raster and parameter table for riparian buffer. 
        
        It finds all parts of the buffer in each subbasin and corresponding drainage area. And then summarize the paramters. 

        Replace Plugin VFSandRBS
        """

        row, col, x, y = 0, 0, 0, 0
        z = 0.0
        i, c = 0, 0
        flag = False
        flowDir = 0.0

        rows = flow_dir_raster.configs.rows,
        cols = flow_dir_raster.configs.columns
        riparian_buffer_nodata = riparian_buffer_raster.configs.nodata
        subbasin_nodata = subbasin_raster.configs.nodata

        riparian_buffer_drainage_area_raster = self.wbe.new_raster(flow_dir_raster.configs)
        riparian_buffer_parts_raster = self.wbe.new_raster(flow_dir_raster.configs)

        #flag if the cells has been traced
        flag2D = np.zeros((rows, cols), dtype=bool)

        path = []
        pathInside = []
        vfsOrRbsDrain = {}
        vfsOrRbsInside = {}
        vfsOrRbsLength = {}
        celldist = (riparian_buffer_raster.configs.resolution_x + riparian_buffer_raster.configs.resolution_y) / 2.0

        for row in range(rows):
            for col in range(cols):
                if subbasin_raster[row, col] != subbasin_nodata and not flag2D[row, col]:
                    path = []
                    pathInside = []

                    x = col
                    y = row

                    path.append((y, x))

                    flag = True
                    length = 0.0

                    while flag:
                        flowDir = flow_dir_raster[y, x]
                        if flowDir > 0:
                            dx, dy = RasterExtension.flow_dir_xy_delta_dic(flowDir)

                            lastVFSorRBSID = riparian_buffer_raster[y, x]
                            isVisited = flag2D[y, x]

                            if lastVFSorRBSID != riparian_buffer_nodata and not isVisited:
                                pathInside.append((y, x))
                                length += celldist * (1.41421356 if c in [1, 4, 16, 64] else 1)

                            #get x,y for downstream cell
                            x += dx
                            y += dy

                            #check to see if the next cell is edge, different riparian buffer. If yes, add it to the list
                            if (riparian_buffer_raster[y, x] == riparian_buffer_nodata or riparian_buffer_raster[y, x] != lastVFSorRBSID or flow_dir_raster[y, x] == 0) and lastVFSorRBSID != riparian_buffer_nodata:
                                #recalculate the current position
                                loc = (y - dy, x - dx)

                                if loc in vfsOrRbsDrain:
                                    vfsOrRbsDrain[loc].extend(path)
                                else:
                                    vfsOrRbsDrain[loc] = path.copy()

                                if loc in vfsOrRbsInside:
                                    vfsOrRbsInside[loc].extend(pathInside)
                                else:
                                    vfsOrRbsInside[loc] = pathInside.copy()

                                if loc in vfsOrRbsLength:
                                    vfsOrRbsLength[loc] = max(length, vfsOrRbsLength[loc])
                                else:
                                    vfsOrRbsLength[loc] = length
                                break

                            if not isVisited:
                                path.append((y, x))
                        else:
                            flag = False

                    #update the flag
                    for loc in path:
                        flag2D[loc[0], loc[1]] = True

        #create the resulting parameter dictionary
        riparain_buffer_parameter_df = pd.DataFrame(columns=['ID','RIBUF','Subbasin','Area_ha','Drainage_Area','Area_Ratio','Length'])
        riparain_buffer_parameter_df.set_index('ID', inplace=True)        

        cellArea = riparian_buffer_raster.configs.resolution_x * riparian_buffer_raster.configs.resolution_y
        vfsOrRbsPartID = 0
        for outLoc in vfsOrRbsDrain.keys():
            vfsOrRbsPartID += 1

            vfsOrRbsID = int(riparian_buffer_raster[outLoc[0], outLoc[1]])
            subID = int(subbasin_raster[outLoc[0], outLoc[1]])
            drainageArea = len(vfsOrRbsDrain[outLoc]) * cellArea / 10000
            length = vfsOrRbsLength[outLoc]

            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'RIBUF'] = vfsOrRbsID
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Subbasin'] = subID
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Drainage_Area'] = drainageArea
            riparain_buffer_parameter_df.loc[vfsOrRbsPartID,'Length'] = length

            for loc in vfsOrRbsDrain[outLoc]:
                riparian_buffer_drainage_area_raster[loc[0], loc[1]] = vfsOrRbsPartID

            for loc in vfsOrRbsInside[outLoc]:
                riparian_buffer_parts_raster[loc[0], loc[1]] = vfsOrRbsPartID

        riparain_buffer_parameter_df["Width"] = width
        riparain_buffer_parameter_df["Area_ha"] = width * riparain_buffer_parameter_df['Length'] * 0.0001
        riparain_buffer_parameter_df["Area_Ratio"] = riparain_buffer_parameter_df["Drainage_Area"] / riparain_buffer_parameter_df["Area_ha"]
        riparain_buffer_parameter_df["VegetationID"] = 6

        #get slope, soil_k, soil_porosity and root_depth using the zone statistics
        slope_df = RasterExtension.get_zonal_statistics(slope_radius_raster / 100, riparian_buffer_parts_raster, "mean","Slope")
        k_df = RasterExtension.get_zonal_statistics(soil_k_raster, riparian_buffer_parts_raster, "mean","Sol_K")
        prosity_df = RasterExtension.get_zonal_statistics(soil_porosity_raster, riparian_buffer_parts_raster, "mean","Sol_porosity")
        root_depth_df = RasterExtension.get_zonal_statistics(landuse_rootdepth_raster, riparian_buffer_parts_raster, "mean","Root_Depth")

        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(slope_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(k_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(prosity_df, left_index=True, right_index=True, how="inner")
        riparain_buffer_parameter_df = riparain_buffer_parameter_df.merge(root_depth_df, left_index=True, right_index=True, how="inner")

        #add other columns with default values
        riparain_buffer_parameter_df["Scenario"] = 1
        riparain_buffer_parameter_df["Year"] = 0

        #adjust the sequence of the columns
        riparain_buffer_parameter_df.reset_index(inplace=True)
        riparain_buffer_parameter_df = riparain_buffer_parameter_df[['Scenario','ID','Year','RIBUF_ID','Subbasin','VegetationID','Length','Width','Area_ha','Drainage_Area','Area_Ratio','Slope','Sol_k','Sol_porosity','Root_Depth']]

        #save to bmp database
        self.save_table(RiparianBuffer.__tablename__, riparain_buffer_parameter_df)

