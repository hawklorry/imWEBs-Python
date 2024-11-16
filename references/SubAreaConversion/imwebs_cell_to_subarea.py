# %%
#create subarea shapefile with subbasin and field

# %%
import geopandas as gpd
import pandas as pd
import os
from rasterstats import zonal_stats
import numpy as np
import whitebox
import h5py
import sqlite3
import json

# %%
# ************ MAKE CHANGE HERE ************
#here are the inputs to the procedure

#field shapefile
field_shp = r"D:\imWEBs\reference_models_and_tools\models\IndianFarm\IFC_shapefiles\field.shp"
#the field id column in field shapefile
field_id_col = "VALUE_"        

#cell-based model folder, it should have following folder
#1. watershed include input and output used by imwebs interface
#2. parameter.db3
#3. scenario which has all model files (file.in, file.out, config.fig, bmp.db3, parameter.h5)
imwebs_cell_model_path = r"D:\imWEBs\cell_subarea_conversion\model\Indian Farm"
imwebs_cell_scenario_name = "scen_00_baseline"
scenario_id = 2

#tools folder
#it should have following tools
#1. imwebs
#2. imwebs_h5
#3. imwebs_input_tool
#4. Parameter_DB_subarea.csv
tools_path = r"D:\imWEBs\cell_subarea_conversion\final\tools"

# %%
# ************ DON'T CHANGE FROM HERE ************

#utility program location
hdf5_util_path = os.path.join(tools_path, "imwebs_h5")
imwebs_main_path = os.path.join(tools_path, "imwebs")
imwebs_input_tool = os.path.join(tools_path, "imwebs_input_tool")
parameter_db_subarea_csv = os.path.join(tools_path, "Parameter_DB_subarea.csv")

#structure bmp lookup table
structure_bmp_lookup_table = {  (5,"parts"):"SubareaRiparianBufferLookup", 
                                (5,"drainage"):"SubareaRiparianBufferDrainageLookup",
                                (19,"parts"):"SubareaTileDrainLookup",
                                (41,"parts"):"SubareaWascobLookup", 
                                (41,"drainage"):"SubareaWascobDrainageLookup",
                                (29,"parts"):"SubareaFeedlotLookup", 
                                (29,"drainage"):"SubareaFeedlotDrainageLookup",
                                (27,"parts"):"SubareaManureStorageLookup"}

# %%
def create_output_folders():
    """
    create output folders to have the final and intermiedate files
    """
    output_path = os.path.join(imwebs_cell_model_path, "output")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    output_path_subarea = os.path.join(imwebs_cell_model_path, "output","1.subarea")
    if not os.path.exists(output_path_subarea):
        os.makedirs(output_path_subarea)

    output_path_landuse_soil = os.path.join(imwebs_cell_model_path, "output","2.landuse_soil")
    if not os.path.exists(output_path_landuse_soil):
        os.makedirs(output_path_landuse_soil)

    output_path_h5_export = os.path.join(imwebs_cell_model_path, "output","3.h5_export")
    if not os.path.exists(output_path_h5_export):
        os.makedirs(output_path_h5_export)

    return output_path, output_path_subarea, output_path_landuse_soil,output_path_h5_export

# %%
#create output pat for all intermediate files
output_path, output_path_subarea, output_path_landuse_soil,output_path_h5_export = create_output_folders()

#don't change from here for same scenario
#----------------------------------------------------------------------------------------
imweb_watershed_output_path     = os.path.join(imwebs_cell_model_path, "watershed","output")
imweb_watershed_input_path      = os.path.join(imwebs_cell_model_path, "watershed","input")

subbasin_shp                    = os.path.join(imweb_watershed_output_path,"subbasin.shp")
landuse_dep                     = os.path.join(imweb_watershed_output_path, 'landuse.dep')
soil_dep                        = os.path.join(imweb_watershed_output_path, 'soil.dep')

dem_dep                         = os.path.join(imweb_watershed_output_path,"dem_mdfy.dep")
slope_dep                       = os.path.join(imweb_watershed_output_path,"slope.dep")

imwebs_cell_scenario_path       = os.path.join(imwebs_cell_model_path, imwebs_cell_scenario_name)
parameterh5                     = os.path.join(imwebs_cell_scenario_path, "parameter.h5")
subarea_data_path               = os.path.join(imwebs_cell_scenario_path, "SubareaData")
bmp_db3_path                    = os.path.join(imwebs_cell_scenario_path, "bmp.db3")
parameter_db3_path              = os.path.join(imwebs_cell_model_path,"database", "parameter.db3")

#id column
subbasin_id_col = "VALUE"

# %%
#used to remove subareas that are too small which depends on cell size
subarea_min_area_ha = 0.0001

#don't change anything from here
#----------------------------------------------------------------------------------------

#output files
subarea_csv         = os.path.join(output_path, 'subarea.csv')
subarea_shp         = os.path.join(output_path_subarea, 'subarea.shp')
subarea_dep         = os.path.join(output_path_subarea, "subarea.dep")
dem_tif             = os.path.join(output_path_subarea,"dem.tif")
slope_tif           = os.path.join(output_path_subarea,"slope.tif")

cell_subarea_csv    = os.path.join(output_path, 'CellSubarea.csv')

subarea_landuse_csv = os.path.join(output_path, 'SubareaLanduseType.csv')
subarea_soil_csv    = os.path.join(output_path, 'SubareaSoilType.csv')
landuse_shp         = os.path.join(output_path_landuse_soil, 'landuse.shp')
soil_shp            = os.path.join(output_path_landuse_soil, 'soil.shp')
subarea_landuse_shp = os.path.join(output_path_landuse_soil, 'subarea_landuse.shp')
subarea_soil_shp    = os.path.join(output_path_landuse_soil, 'subarea_soil.shp')



#fixed column name, don't change

#for subarea.csv
subarea_id_col = "Id"
subarea_field_id_col = "FieldId"
subarea_subbasin_id_col = "SubbasinId"
subarea_area_col = "Area"
subarea_slope_col = "Slope"
subarea_elevation_col = "Elevation"

#for land use and soil
landuse_type_col = "VALUE"
soil_type_col = "VALUE"

lanuse_soil_subrea_id_col = "SubAreaId"
lanuse_soil_subarea_landuse_type_col = "LanduseTypeId"
lanuse_soil_subarea_soil_type_col = "SoilTypeId"

#columns in CellSubarea.csv
cell_subarea_cell_index_col = "CellIndex"
cell_subarea_subarea_id_col = "SubareaId"

# %%
def whitebox_to_shapefile(whitebox_dep, shp):
    """
    convert whitebox dep file to shapefile 

    Parameters
    ----------
    whitebox_dep    : the file path of whitebox dep file
    shp             : the file path of converted shapefile

    Returns
    ----------
    NONE
    
    """
    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    wbt.raster_to_vector_polygons(whitebox_dep,shp)

def whitebox_raster_format(source_raster, desti_raster):
    """
    convert raster froom source format to destination format

    Parameters
    ----------
    source_raster   : the file path of source raster
    desti_raster    : the file path of destination raster

    Returns
    ----------
    NONE
    
    """
    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    wbt.convert_raster_format(source_raster,desti_raster) 


# %%
def add_dep_to_parameterh5(dep_file, h5_file):
    """
    add dept to parameter.h5
    """
    cwd = os.getcwd()
    os.chdir(hdf5_util_path)
    cmd = ['java',
            '-D"java.library.path"="'+hdf5_util_path+'\lib"',
            '-jar',
            'IMWEBsHDF5Util.jar',
            'save-raster-to-h5',
            '"'+dep_file+'"',
            '"'+h5_file+'"']
    print(" ".join(cmd))
    os.system(" ".join(cmd))
    os.chdir(cwd)

def export_parameterh5_item(itemName):
    """
    export item from parameter h5
    """
    with h5py.File(parameterh5, 'r') as h5_file:
        for group in h5_file.keys():
            for ds_name in h5_file[group].keys():               
                if ds_name == itemName:
                    try:
                        #print(ds_name)
                        ds_data = h5_file[group][ds_name]
                        np_array = np.array(ds_data, dtype='f')
                        np.savetxt(os.path.join(output_path_h5_export, ds_name+".txt"), np_array, fmt='%f', delimiter='\t')
                        return True
                    except:
                        continue
                    break
        
    return False

# %%
def generate_subaera():
    """
    generate subarea shapefile with subbasin and field shapefile

    Returns
    -------
    DataFrame for subarea
    
    """
    #read shapefile and restructure the columns
    field_shp_df = gpd.read_file(field_shp)
    field_shp_df[subarea_field_id_col] = field_shp_df[field_id_col].astype(int)    
    field_shp_df.sort_values(by = subarea_field_id_col, inplace=True)

    subbasin_shp_df = gpd.read_file(subbasin_shp)
    subbasin_shp_df[subarea_subbasin_id_col] = subbasin_shp_df[subbasin_id_col].astype(int)
    subbasin_shp_df.drop(subbasin_id_col, axis=1, inplace=True)
    subbasin_shp_df.sort_values(by = subarea_subbasin_id_col, inplace=True)

    #identify
    subarea_shp_df = gpd.overlay(subbasin_shp_df, field_shp_df, how='identity')

    #add area in ha
    subarea_shp_df[subarea_area_col] = subarea_shp_df.area / 10000

    #remove subareas that are two small
    subarea_shp_df = subarea_shp_df[subarea_shp_df[subarea_area_col] > subarea_min_area_ha]

    #add subarea id
    subarea_shp_df.reset_index(inplace=True)
    subarea_shp_df[subarea_id_col] = subarea_shp_df.index + 1

    #remove columns that are not necessary. These columns may cause problems in following steps.
    subarea_shp_df.drop([col for col in subarea_shp_df.columns if col not in [subarea_field_id_col, subarea_area_col, subarea_id_col, subarea_subbasin_id_col, 'geometry']], axis=1, inplace=True)

    #save to shapefile
    subarea_shp_df.to_file(subarea_shp, index = False)

    #convert to dep
    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    wbt.vector_polygons_to_raster(subarea_shp,subarea_dep, field = subarea_id_col, nodata = True, base = dem_dep) 

    #return the dataframe
    return subarea_shp_df

# %%
def get_subarea_raster_average(subarea_shp, raster, col_name):
    """
    get average value for each subbarea

    Parameters
    ----------
    subarea_shp : the file path of subarea shapefile
    raster      : the file path of statistic raster 
    col_name    : the column name

    Returns
    -------
    DataFrame with two columns:
    1. SubAreaId - SubArea ID
    2. col_name - The statistic value
    
    """
    stats = zonal_stats(subarea_shp, raster, band=1,stats='mean', geojson_out = True)

    subarea_mean = {}
    for land in stats:
        #skip if majority is none
        if land['properties'][subarea_id_col] is None:
            continue
        elif land['properties']['mean'] is None:
            subarea_mean[int(land['properties'][subarea_id_col])] = None
        else:
            subarea_mean[int(land['properties'][subarea_id_col])] = land['properties']['mean']
    
    #create dataframe and save the original crop id to Original ID column
    df = pd.DataFrame.from_dict(subarea_mean, orient = 'index', columns = [col_name])
    df.index.name = subarea_id_col
    df = df.sort_index()
    df = df.reset_index()

    #fill the null values
    df = df.fillna(method="ffill")

    return df

# %%
def generate_subarea_csv():
    """
    generate subarea.csv with subarea id, subbasin id, field id, area, slope and elevation
    """
    print("Generating subarea ... ")
    subarea_shp_df = generate_subaera()

    print("Calculating subarea elevation ... ")
    whitebox_raster_format(dem_dep, dem_tif)
    elevation_df = get_subarea_raster_average(subarea_shp, dem_tif, subarea_elevation_col)
    subarea_shp_df = subarea_shp_df.merge(elevation_df, on = subarea_id_col, how = "left")

    print("Calculating subarea slope ... ")
    whitebox_raster_format(slope_dep, slope_tif)
    slope_df = get_subarea_raster_average(subarea_shp, slope_tif, subarea_slope_col)
    subarea_shp_df = subarea_shp_df.merge(slope_df, on = subarea_id_col, how = "left")

    #save to subarea.csv
    subarea_shp_df.to_csv(subarea_csv, columns=[subarea_id_col, subarea_subbasin_id_col, subarea_field_id_col, subarea_area_col, subarea_slope_col, subarea_elevation_col],index = False)

    #return number of subarea
    return len(subarea_shp_df)

# %%
def generate_cell_subarea_csv():
    """
    generate CellSubarea.csv
    """
    print("Generating CellSubarea.csv ...")
    add_dep_to_parameterh5(subarea_dep, parameterh5)
    export_parameterh5_item('subarea')
    
    cell_subarea_df = pd.read_csv(os.path.join(output_path_h5_export,"subarea.txt"),names=[cell_subarea_subarea_id_col])
    cell_subarea_df.index.name = cell_subarea_cell_index_col
    cell_subarea_df.to_csv(cell_subarea_csv)

# %%
def generate_subarea_soil_landuse_shapefile(subarea_shp, landuse_soil_shp, subarea_landuse_soil_shp):
    """
    get subarea landuse or soil

    Parameters
    ----------
    subarea_shp                 : the file path of subarea shapefile
    landuse_soil_shp            : the file path of landuse/soil shapefile 
    subarea_landuse_soil_shp    : the file path of subarea landuse/soil shapefile

    Returns
    -------
    NONE

    """
    subarea_shp_df = gpd.read_file(subarea_shp)
    landuse_soil_shp_df = gpd.read_file(landuse_soil_shp)

    #identify
    subarea_landuse_soil_shp_df = gpd.overlay(subarea_shp_df, landuse_soil_shp_df, how='identity')
    subarea_landuse_soil_shp_df.to_file(subarea_landuse_soil_shp)

def generate_subarea_soil_landuse_csv(subarea_landuse_soil_shp, source_landuse_soil_col, result_landuse_soil_col, landuse_soil_csv):
    """
    generate subarea soil/land use csv (SubareaLanduseType.csv and SubareaSoilType.csv) 

    Parameters
    ----------
    subarea_landuse_soil_shp    : the file path of subarea landuse/soil shapefile
    source_landuse_soil_col     : the column name of landuse/soil type id in landuse/soil shapefile
    result_landuse_soil_col     : the column name of landuse/soil type id in result csv file
    landuse_soil_csv            : the file path of the subarea landuse/soil csv file

    """ 
    #read
    subarea_landuse_soil_shp_df = gpd.read_file(subarea_landuse_soil_shp)

    #add area in ha
    subarea_landuse_soil_shp_df[subarea_area_col] = subarea_landuse_soil_shp_df.area / 10000

    #rename the id column
    subarea_landuse_soil_shp_df.rename(columns={subarea_id_col:lanuse_soil_subrea_id_col}, inplace= True)
    subarea_landuse_soil_shp_df.rename(columns={source_landuse_soil_col:result_landuse_soil_col}, inplace= True)
  
    #save to csv
    subarea_landuse_soil_shp_df.to_csv(landuse_soil_csv, columns=[lanuse_soil_subrea_id_col, result_landuse_soil_col, subarea_area_col], index = False)

    #fill na
    df = pd.read_csv(landuse_soil_csv)
    df[result_landuse_soil_col] = df[result_landuse_soil_col].fillna(method="ffill")
    df.to_csv(landuse_soil_csv, index = False)

def generate_subarea_soil_landuse():
    """
    generate subarea soil and landuse csv file
    """
    print("Generating SubareaLanduseType.csv ...")
    whitebox_to_shapefile(landuse_dep, landuse_shp)
    generate_subarea_soil_landuse_shapefile(subarea_shp, landuse_shp, subarea_landuse_shp)
    generate_subarea_soil_landuse_csv(subarea_landuse_shp, landuse_type_col, lanuse_soil_subarea_landuse_type_col, subarea_landuse_csv)
    
    print("Generating SubareaSoilType.csv ...")
    whitebox_to_shapefile(soil_dep, soil_shp)
    generate_subarea_soil_landuse_shapefile(subarea_shp, soil_shp, subarea_soil_shp)
    generate_subarea_soil_landuse_csv(subarea_soil_shp, soil_type_col, lanuse_soil_subarea_soil_type_col, subarea_soil_csv)


# %%
def run_imwebs():
    #run imwebs main
    cwd = os.getcwd()
    os.chdir(imwebs_main_path)
    cmd = ['imwebsmain',
            f'"{imwebs_main_path}"',
            f'"{imwebs_cell_scenario_path}"',
            f'{scenario_id}']
    print(" ".join(cmd))
    os.system(" ".join(cmd))
    os.chdir(cwd)

def export_text_file_from_cell_model(numOfSubarea):
    """
    export text files from cell-based model to SubareaData folder
    """
    print("Exporting text file from cell-based model ...")
    #create subareadata folder    
    output_path_cell_text_files = os.path.join(imwebs_cell_scenario_path, "SubareaData")
    if not os.path.exists(output_path_cell_text_files):
        os.makedirs(output_path_cell_text_files)

    #add flags in file.in
    file_in_file = os.path.join(imwebs_cell_scenario_path, "file.in")
    with open(file_in_file,"r") as f:
        lines = f.readlines()
    
    if "VERSIONTYPE" not in lines[0]:
        lines.insert(0, "VERSIONTYPE|0\n")
    else:
        lines[0] = "VERSIONTYPE|0\n"

    if "ISPREPAREFORSUBAREAINPUT" not in lines[1]:
        lines.insert(1, "ISPREPAREFORSUBAREAINPUT|1\n")
    else:
        lines[1] = "ISPREPAREFORSUBAREAINPUT|1\n"
        
    if "SUBAREANUMBER" not in lines[4]:
        lines.insert(4, f"SUBAREANUMBER|{numOfSubarea}\n")  
    else:
        lines[4] = f"SUBAREANUMBER|{numOfSubarea}\n"    
    
    with open(file_in_file,"w") as f:
        f.writelines(lines)


    run_imwebs()

# %%
def export_weight():
    print("Exporting weights ...")
    export_parameterh5_item("weight_t")
    export_parameterh5_item("weight_p")
    export_parameterh5_item("weight_w")
    export_parameterh5_item("weight_pet")

# %%
#subarea data file name to average column name dictionary
file_column_dic = {
    'usle_p.txt':'USLE_P',
    'moist_in.txt':'MoistureInitial',
    'flow_acc.txt':'FlowAccumulationAverage',
    'wetland.txt':'WetlandFraction',
    'IUH002Yr_t0s.txt':'TravelTimeAverage2',
    'IUH010Yr_t0s.txt':'TravelTimeAverage10',
    'IUH100Yr_t0s.txt':'TravelTimeAverage100',
    'IUH002Yr_delta_t.txt':'TravelTimeStd2',
    'IUH010Yr_delta_t.txt':'TravelTimeStd10',
    'IUH100Yr_delta_t.txt':'TravelTimeStd100'
}

def getColumnFromFile(filename):
    if filename in file_column_dic:
        return file_column_dic[filename]
    return "unknown"

def calculate_subarea_parameters():
    #read all cell-parameters from text files and calculate the average for each subarea
    print("Calculating Subarea parameters ...")

    #check
    if len(os.listdir(subarea_data_path)) == 0:
        print("The cell-based model parameters are not exported correctly!")
        exit

    cell_subarea_df = pd.read_csv(cell_subarea_csv)

    for subarea_data_file in os.listdir(subarea_data_path):
        if ".txt" not in subarea_data_file:
            continue

        #print(subarea_data_file)

        df = pd.read_csv(os.path.join(subarea_data_path, subarea_data_file), skip_blank_lines=True, names = [getColumnFromFile(subarea_data_file)], delim_whitespace = True, na_values = '-nan(ind)')
        df.index.name = cell_subarea_cell_index_col
        
        cell_subarea_df = cell_subarea_df.merge(df, on = cell_subarea_cell_index_col, how = "left")

    #set -32768 to null
    cell_subarea_df = cell_subarea_df.replace({-32768: np.nan})

    #get subarea average
    average_df = pd.pivot_table(cell_subarea_df, values=list(file_column_dic.values()), index=cell_subarea_subarea_id_col, aggfunc=np.average)
    average_df = average_df.replace({np.nan: 0.0})
    average_df.index.name = subarea_id_col

    #merge with id column
    subarea_csv_df = pd.read_csv(subarea_csv)
    subarea_csv_df = subarea_csv_df.merge(average_df, on = subarea_id_col, how = "left")

    #add TopographyWeight and LateralWidth
    subarea_csv_df["TopographyWeight"] = 1
    subarea_csv_df["LateralWidth"] = np.sqrt(subarea_csv_df["Area"] * 10000)/10

    #add value for missing subarea in CellSubarea.csv
    subarea_csv_df = subarea_csv_df.fillna(method="ffill")

    #save to file
    subarea_csv_df.to_csv(subarea_csv, index= False)

def save_csv_to_bmp(csv_file):
    #save the csv to bmp database
    with sqlite3.connect(bmp_db3_path) as conn:
        tablename = str(os.path.basename(csv_file)).split('.')[0]
        
        cursor = conn.cursor()
        cursor.executescript(f'DROP TABLE IF EXISTS {tablename}')
        conn.commit()
        cursor.close()  

        csv_df = pd.read_csv(csv_file)
        csv_df.to_sql(tablename, conn, if_exists='replace', index = False)

def import_subarea_parameter_to_bmp_db3():
    #save the csv to bmp database
    print("Importing CSVs (SubArea, CellSubarea, SubareaLanduseType, SubareaSoilType) to bmp.db3 ...")
    
    save_csv_to_bmp(subarea_csv)
    save_csv_to_bmp(cell_subarea_csv)
    save_csv_to_bmp(subarea_soil_csv)
    save_csv_to_bmp(subarea_landuse_csv)

# %%
def generate_structure_bmp_lookup_table():
    with sqlite3.connect(bmp_db3_path) as conn:
        df = pd.read_sql("select * from BMP_scenarios where BMP = 5", con=conn) # or BMP = 19 or BMP = 41 or BMP = 29 or BMP = 27
        for index in df.index:
            bmpid = int(df.loc[index]['BMP'])
            dis = str(df.loc[index]['DISTRIBUTION']).split('/')

            if len(dis) == 1:
                generate_structure_bmp_lookup_table_drainage_part(dis[1], get_structure_bmp_lookup_table_name(bmpid, "parts"))
            elif len(dis) > 1:
                generate_structure_bmp_lookup_table_drainage_part(dis[0], get_structure_bmp_lookup_table_name(bmpid, "drainage"))
                generate_structure_bmp_lookup_table_drainage_part(dis[1], get_structure_bmp_lookup_table_name(bmpid, "parts"))
            
def get_structure_bmp_lookup_table_name(bmpid, drainage_parts):
    return structure_bmp_lookup_table[(bmpid, drainage_parts)]

def generate_structure_bmp_lookup_table_drainage_part(item_name, subareaLookupName):
    print(f"Generating lookup table for {item_name}")

    #export to text file
    exported = export_parameterh5_item(item_name)

    #if the h5 item is not found, stop here
    if not exported:
        exit

    #cell subare lookup table
    cell_subarea_df = pd.read_csv(cell_subarea_csv)

    #get number of cells of each subarea - c
    subarea_count = cell_subarea_df[cell_subarea_df[cell_subarea_subarea_id_col] > 0][cell_subarea_subarea_id_col].value_counts()
    subarea_cell_count_df = subarea_count.to_frame(name = "SubAreaCellCount")
    subarea_cell_count_df.index.name = cell_subarea_subarea_id_col

    #cell riparian buffer/vegetative filter strip part file export from h5 file
    cell_part_txt_path = os.path.join(output_path_h5_export, f'{item_name}.txt')
    cell_part_df = pd.read_csv(cell_part_txt_path, skip_blank_lines=True, names = ["PartId"], delim_whitespace = True)
    cell_part_df.index.name = "CellIndex"
        
    #get number of cells of each part - b
    part_count = cell_part_df[cell_part_df['PartId'] > 0]['PartId'].value_counts()
    part_cell_count_df = part_count.to_frame(name = "PartCellCount")
    part_cell_count_df.index.name = "PartId"

    # get number of unique combination of subarea and part - a
    cell_subarea_part_df = cell_subarea_df.merge(cell_part_df, on = cell_subarea_cell_index_col, how = "left")
    subarea_part_count_df = pd.pivot_table(cell_subarea_part_df[(cell_subarea_part_df[cell_subarea_subarea_id_col] > 0) & (cell_subarea_part_df['PartId'] > 0)], values=cell_subarea_cell_index_col, index=[cell_subarea_subarea_id_col,'PartId'], aggfunc='count')
    subarea_part_count_df.reset_index(inplace=True)
    subarea_part_count_df = subarea_part_count_df.rename(columns={cell_subarea_cell_index_col:"SubAreaPartCellCount"})

    #merge part and subarea count
    subarea_part_count_df = subarea_part_count_df.merge(part_cell_count_df, on = "PartId", how = "left")
    subarea_part_count_df = subarea_part_count_df.merge(subarea_cell_count_df, on = cell_subarea_subarea_id_col, how = "left")

    #do the calculation
    subarea_part_count_df["FractionToBmp"] = np.round(subarea_part_count_df["SubAreaPartCellCount"] / subarea_part_count_df["PartCellCount"], decimals=4)
    subarea_part_count_df["FractionToSubarea"] = np.round(subarea_part_count_df["SubAreaPartCellCount"] / subarea_part_count_df["SubAreaCellCount"], decimals=4)

    #output
    subarea_part_count_df["LocationId"] = subarea_part_count_df["PartId"]
    riparian_buffer_lookup_csv_path = os.path.join(output_path,f'{subareaLookupName}.csv')
    subarea_part_count_df.to_csv(riparian_buffer_lookup_csv_path, columns=[cell_subarea_subarea_id_col, "LocationId", "FractionToBmp", "FractionToSubarea"], index=False)

    #save to bmp
    save_csv_to_bmp(riparian_buffer_lookup_csv_path)


# %%
def import_parameter_db_subarea():
    """
    import Parameter_DB_subarea.csv
    """
    print("Importing Parameter_DB_subarea.csv ...")

    with sqlite3.connect(parameter_db3_path) as conn:   
        csv_df = pd.read_csv(parameter_db_subarea_csv)
        csv_df.to_sql("Subarea", conn, if_exists='replace', index = False)

# %%
def modify_appsettings_json():
    """
    modify appsettings.json
    """
    appsettings_file = os.path.join(imwebs_input_tool, "appsettings.json")
    with open(appsettings_file, 'r+') as f:
        data = json.load(f)
    
    data["Outputs"]["OutputDbPath"] = os.path.join(imwebs_cell_model_path, "database","Parameter_subarea.db3")
    data["Inputs"]["BmpDbPath"] = bmp_db3_path
    data["Inputs"]["HydroClimateDbPath"] = os.path.join(imwebs_cell_model_path, "database","HydroClimate.db3")
    data["Inputs"]["ParameterDbPath"] = parameter_db3_path
    data["Inputs"]["WeightInputs"][0]["WeightFilePath"] = os.path.join(output_path_h5_export,"weight_p.txt")
    data["Inputs"]["WeightInputs"][1]["WeightFilePath"] = os.path.join(output_path_h5_export,"weight_pet.txt")
    data["Inputs"]["WeightInputs"][2]["WeightFilePath"] = os.path.join(output_path_h5_export,"weight_t.txt")
    data["Inputs"]["WeightInputs"][3]["WeightFilePath"] = os.path.join(output_path_h5_export,"weight_w.txt")

    with open(appsettings_file, 'w') as f:
        json.dump(data, f, indent=4)

def run_imwebs_input_tool(para):
    """
    add dept to parameter.h5
    """
    cwd = os.getcwd()
    os.chdir(imwebs_input_tool)
    cmd = ['ImwebsSubarea.Input.CLI.exe',
            para]
    print(" ".join(cmd))
    os.system(" ".join(cmd))

    os.chdir(cwd)

def create_parameter_subarea_db3():
    print("Creating Parameter_subarea.db3 ...")
    modify_appsettings_json()

    print("Converting base ...")
    run_imwebs_input_tool("base-conversion-all")

    print("Converting bmp ...")
    run_imwebs_input_tool("bmp-conversion-all")

# %%
def change_file_in_version_type_to_1():
    print("Changing file.in versiontype to 1 ...")

    #add flags in file.in
    file_in_file = os.path.join(imwebs_cell_scenario_path, "file.in")
    with open(file_in_file,"r") as f:
        lines = f.readlines()
    
    if "VERSIONTYPE" in lines[0]:
        lines[0] = lines[0].replace("0","1")
    
    with open(file_in_file,"w") as f:
        f.writelines(lines)

# %%
num_subarea = generate_subarea_csv()
generate_cell_subarea_csv()
generate_subarea_soil_landuse()
export_text_file_from_cell_model(num_subarea)
export_weight()
calculate_subarea_parameters()
import_subarea_parameter_to_bmp_db3()
generate_structure_bmp_lookup_table()
import_parameter_db_subarea()
create_parameter_subarea_db3()
change_file_in_version_type_to_1()
run_imwebs()

print("Done")

# %%



