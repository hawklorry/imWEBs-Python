import h5py
import os
import shutil
import subprocess
from ..names import Names
from whitebox_workflows import WbEnvironment, Raster
import numpy as np
import pandas as pd

import logging
logger = logging.getLogger(__name__)

class ParameterH5:

    CHUNK_SIZE = 10000

    RASTERS = ["dem","flow_acc","flow_dir","landuse", 
               "moist_in","slope","soil","stream_network",
               "stream_order","subbasin","usle_p","wetland"]



    def __init__(self, parameter_h5_file) -> None:
        if not os.path.exists(parameter_h5_file):
            with h5py.File(self.parameter_h5_file, 'w') as h5_file:
                pass
        
        self.parameter_h5_file = parameter_h5_file      
        with h5py.File(parameter_h5_file, 'r') as h5_file:
            for group_name in h5_file.keys():
                if group_name == "asc":
                    group = h5_file[group_name]
                    for attr_name, attr_value in group.attrs.items():
                        if attr_name == "CELL_SIZE":
                            self.cell_num = int(attr_value)
                        if attr_name == "DX":
                            self.cell_size = attr_value   

    def get_weight_column_number(self, weight_name:str) -> int:
        with h5py.File(self.parameter_h5_file, 'r') as h5_file:
            path = f"weight/{weight_name}"
            if path not in h5_file:
                return -1

            return h5_file[path].shape[1]    

    def get_weight(self, weight_name:str, station_index:int) -> pd.DataFrame:
        with h5py.File(self.parameter_h5_file, 'r') as h5_file:
            path = f"weight/{weight_name}"
            if path not in h5_file:
                return None            
            
            if station_index >= h5_file[path].shape[1]:
                return None
            
            #read the id and weight for the station 
            weight_data = h5_file[path][:,station_index]

            #create data frame with station id starts from 1         
            df_weight = pd.DataFrame(weight_data, columns=["Weight"])
            df_weight["SubareaId"] = df_weight.index + 1 #assuming the id starts from 1
            df_weight["ClimateStationId"] = station_index + 1

            return df_weight


    def duplicate(self, from_path:str, to_path:str):
        """
        duplicate from from_path to to_path
        """
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if from_path in h5_file:
                h5_file.copy(from_path, to_path)
            else:
                raise ValueError(f"Couldn't find {from_path} in {self.parameter_h5_file}.")

    def add_rasters(self, raster_folder:str):
        """
        add rasters to asc group
        """

        logger.info("Adding rasters to parameter.h5")

        #mask
        mask_raster_file = os.path.join(raster_folder,"mask.tif")
        if not os.path.exists(mask_raster_file):
            raise ValueError(f"mask raster is not available.")
        
        wbe = WbEnvironment()
        mask_raster = wbe.read_raster(mask_raster_file)

        cell_size = self.__add_raster_mask2(mask_raster)
        self.__add_raster_mask1(mask_raster)
        self.__add_raster_mask_metadata(mask_raster, cell_size)

        flow_dir_raster = None
        flow_acc_raster = None        
        
        for raster_name in ParameterH5.RASTERS + Names.bmp_distributions():
            raster_file = os.path.join(raster_folder, f"{raster_name}.tif")
            if not os.path.exists(raster_file):
                continue
            logger.info(f"   -- {raster_name}")
            raster = wbe.read_raster(raster_file)
            self.__add_raster_non_mask(raster, mask_raster)
            if "flow_dir" == raster_name:
                flow_dir_raster = raster
            if "flow_acc" == raster_name:
                flow_acc_raster = raster

        if flow_dir_raster is None:
            raise ValueError("Couldn't find flow_dir.tif.")

        if flow_acc_raster is None:
            raise ValueError("Couldn't find flow_acc.tif.")
        
        self.__create_flow_path(flow_dir_raster, mask_raster,cell_size)
        self.__create_flow_order()

    def __add_raster_mask_metadata(self, mask_raster:Raster, cell_size:int):
        """
        add mask metadata
        """
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            group = h5_file["asc"]

            group.attrs["CELL_SIZE"] = np.float32(cell_size)
            group.attrs["DX"] = np.float32(mask_raster.configs.resolution_x)
            group.attrs["DY"] = np.float32(mask_raster.configs.resolution_x)
            group.attrs["NROWS"] = np.float32(mask_raster.configs.rows)
            group.attrs["NCOLS"] = np.float32(mask_raster.configs.columns)
            group.attrs["NODATA_VALUE"] = np.float32(mask_raster.configs.nodata)
            group.attrs["XLLCENTER"] = np.float32(mask_raster.configs.west + mask_raster.configs.resolution_x / 2)
            group.attrs["YLLCENTER"] = np.float32(mask_raster.configs.south - mask_raster.configs.resolution_y / 2)
    
    def __add_raster_mask2(self, mask_raster:Raster):
        """
        add mask raster mask 2
        """

        logger.info("   -- mask2")

        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        noddata = mask_raster.configs.nodata
        path = "asc/mask2"

        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if path in h5_file:
                del h5_file[path]

        position_2d = np.full((ParameterH5.CHUNK_SIZE, cols),-1)
        row_index = 0
        row_count = 0
        total_row = 0
        for row in range(rows):            
            total_row += 1
            for col in range(cols):
                if mask_raster[row, col] != noddata:
                    position_2d[row_count, col] = row_index
                    row_index += 1                    

            row_count += 1
            if row_count >= ParameterH5.CHUNK_SIZE:
                with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                    if total_row <= ParameterH5.CHUNK_SIZE:                    
                        h5_file.create_dataset(path, data = position_2d,maxshape=(None, cols), chunks=True)
                    else:
                        h5_file[path].resize((total_row, cols))
                        h5_file[path][total_row - ParameterH5.CHUNK_SIZE:] = position_2d
                row_count = 0
    
        if row_count > 0:
            position_2d = position_2d[:row_count]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= ParameterH5.CHUNK_SIZE:                
                    h5_file.create_dataset(path, data = position_2d)
                else:
                    h5_file[path].resize((total_row, cols))
                    h5_file[path][total_row - row_count:] = position_2d

        return row_index
    
    def __add_raster_mask1(self, mask_raster:Raster):
        """
        add mask raster - mask1
        """

        logger.info("   -- mask1")

        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        noddata = mask_raster.configs.nodata
        path = "asc/mask1"

        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if path in h5_file:
                del h5_file[path]

        position_1d = np.full((ParameterH5.CHUNK_SIZE, 2),-1)
        row_count = 0
        total_row = 0
        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != noddata:
                    position_1d[row_count, 0] = row
                    position_1d[row_count, 1] = col   
                    row_count += 1
                    total_row += 1              

                if row_count >= ParameterH5.CHUNK_SIZE:
                    with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                        if total_row <= ParameterH5.CHUNK_SIZE:                        
                            h5_file.create_dataset(path, data = position_1d,maxshape=(None, 2), chunks=True)
                        else:
                            h5_file[path].resize((total_row, 2))
                            h5_file[path][total_row - ParameterH5.CHUNK_SIZE:] = position_1d
                    row_count = 0
    
        if row_count > 0:
            position_1d = position_1d[:row_count]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= ParameterH5.CHUNK_SIZE:                
                    h5_file.create_dataset(path, data = position_1d)
                else:
                    h5_file[path].resize((total_row, 2))
                    h5_file[path][total_row - row_count:] = position_1d

    def __add_raster_non_mask(self, raster:Raster, mask_raster:Raster):
        """
        add non-mask raster
        """
        """
        add mask raster - mask1
        """
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        noddata = mask_raster.configs.nodata        
        path = f"asc/{raster.get_short_filename().lower()}"

        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if path in h5_file:
                del h5_file[path]   

        raster_data = np.full((ParameterH5.CHUNK_SIZE, 1),-1.0, dtype=np.float32)
        row_count = 0
        total_row = 0
        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != noddata:
                    raster_data[row_count] = raster[row,col]   
                    row_count += 1
                    total_row += 1              

                if row_count >= ParameterH5.CHUNK_SIZE:
                    with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                        if total_row <= ParameterH5.CHUNK_SIZE:                        
                            h5_file.create_dataset(path, data = raster_data,maxshape=(None, 1), chunks=True)
                        else:
                            h5_file[path].resize((total_row, 1))
                            h5_file[path][total_row - ParameterH5.CHUNK_SIZE:] = raster_data
                    row_count = 0
    
        if row_count > 0:
            raster_data = raster_data[:row_count]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= ParameterH5.CHUNK_SIZE:                
                    h5_file.create_dataset(path, data = raster_data)
                else:
                    h5_file[path].resize((total_row, 1))
                    h5_file[path][total_row - row_count:] = raster_data
        
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            h5_file[path].attrs["MIN"] = np.float32(raster.configs.minimum)
            h5_file[path].attrs["MAX"] = np.float32(raster.configs.maximum)

    def __create_flow_order(self):
        """
        basically just sort flow_acc and save original index
        """

        logger.info("   -- flow_order")

        path = "asc/flow_order"
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if path in h5_file:
                del h5_file[path]   

        #read flow_acc
        flow_acc = None
        with h5py.File(self.parameter_h5_file, 'r') as h5_file:
            flow_acc = h5_file["asc/flow_acc"][:,0]  

        #get sorited indices
        sorted_indices = np.argsort(flow_acc, kind="mergesort")

        #save
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:                     
            h5_file.create_dataset(path, data = sorted_indices, dtype = np.float32)

            h5_file[path].attrs["MIN"] = np.float32(sorted_indices.min())
            h5_file[path].attrs["MAX"] = np.float32(sorted_indices.max())

    def __create_flow_path(self, flow_dir_raster:Raster, mask_raster:Raster, cell_size:int):
        """
        find the row index of downstream cell and save it to flow path
        """

        logger.info("   -- flow_path")

        path = "asc/flow_path"
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            if path in h5_file:
                del h5_file[path]    
    
        #read mask2
        mask2 = None
        with h5py.File(self.parameter_h5_file, 'r') as h5_file:
            mask2 = h5_file["asc/mask2"][:]   

        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        dir_to_index = {1:0,2:1,4:2,8:3,16:4,32:5,64:6,128:7}


        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        nodata = mask_raster.configs.nodata

        raster_data = np.full((ParameterH5.CHUNK_SIZE, 1),-2.0, dtype=np.float32)
        row_count = 0
        total_row = 0
        min_value = np.iinfo(np.int32).max
        max_value = np.iinfo(np.int32).min
        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != nodata: 
                    x = col
                    y = row
                    flowDir = flow_dir_raster[y, x]
                    if flowDir > 0:
                        c = dir_to_index[flowDir]
                        x += dX[c]
                        y += dY[c]
                        raster_data[row_count] = mask2[y, x]
                        min_value = min(min_value, int(mask2[y, x]))
                        max_value = max(max_value, int(mask2[y, x]))

                    row_count += 1
                    total_row += 1              

                if row_count >= ParameterH5.CHUNK_SIZE:
                    with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                        if total_row <= ParameterH5.CHUNK_SIZE:                        
                            h5_file.create_dataset(path, data = raster_data,maxshape=(None, 1), chunks=True)
                        else:
                            h5_file[path].resize((total_row, 1))
                            h5_file[path][total_row - ParameterH5.CHUNK_SIZE:] = raster_data
                    row_count = 0
    
        if row_count > 0:
            raster_data = raster_data[:row_count]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= ParameterH5.CHUNK_SIZE:                
                    h5_file.create_dataset(path, data = raster_data)
                else:
                    h5_file[path].resize((total_row, 1))
                    h5_file[path][total_row - row_count:] = raster_data
        
        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
            h5_file[path].attrs["MIN"] = np.float32(min_value)
            h5_file[path].attrs["MAX"] = np.float32(max_value)

    @staticmethod
    def generate_parameter_h5(scenario_folder:str, output_folder:str):
        """
        generate parameter h5 file

        1. Assume all the weight files have been generated in output_folder
        2. run imwebsh5.exe tool to generate parameter.h5 in watershed/output folder
        3. move parameter.h5 to model folder
        4. clean weight files in watershed/output folder
        """

        if not os.path.exists(scenario_folder):
            raise ValueError(f"Couldn't find {scenario_folder}")
        
        if not os.path.exists(output_folder):
            raise ValueError(f"Couldn't find {output_folder}")
        
        #generate the parameter.h5
        imwebs_h5_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine", "imwebsh5.exe")
        if not os.path.exists(imwebs_h5_exe):
            raise ValueError(f"Couldn't find imwebsh5.exe.")        
        result = subprocess.run([imwebs_h5_exe] + [output_folder], capture_output=True, text=True)
        if len(result.stdout) > 0:
            logger.info(result.stdout)        
        if len(result.stderr) > 0:
            logger.info(result.stderr)

        #check if parameter.h5 is generated
        if not os.path.exists(os.path.join(output_folder,Names.parameteH5Name)):
            raise ValueError("parameter.h5 is not generated")

        #copy parameter.h5
        shutil.move(os.path.join(output_folder,Names.parameteH5Name),os.path.join(scenario_folder,Names.parameteH5Name))       


