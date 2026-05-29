from whitebox_workflows import Raster
import pandas as pd
import h5py

class Interpolation:
    CHUNK_SIZE = 10000

    def __init__(self, parameter_h5_file:str, weight_name:str) -> None:
        self.parameter_h5_file = parameter_h5_file
        self.path = f"weight/{weight_name}"

    def write_weight(self, mask_raster:Raster, station_coordinates:list):
        """write weight"""
        pass

    def write_weight_subbarea(self, subarea_centroid_df:pd.DataFrame, station_coordinates:list):
        pass
