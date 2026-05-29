from .interpolation import Interpolation
from .average_uniform import AverageUniform
from .grid_interpolation import GridInterpolation
from .inverse_distance import InverseDistance
from .linear_triangle import LinearTriangle
from .thiessen_polygon import ThiessenPolygon
from whitebox_workflows import Raster
import pandas as pd
import logging
logger = logging.getLogger(__name__)

class Weight:
    def __init__(self, method:str, radius:int, parameter_h5_file:str, weight_name:str,station_coordinates:list):
        self.method = method
        self.radius = radius
        self.parameter_h5_file = parameter_h5_file
        self.weight_name = weight_name
        self.station_coordinates = station_coordinates

        #get interpolation object based on method
        self.interploation = Interpolation(parameter_h5_file, weight_name)
        if method == "average_uniform":
            self.interploation = AverageUniform(parameter_h5_file, weight_name)
        elif method == "grid_interpolation":
            self.interploation = GridInterpolation(parameter_h5_file, weight_name)
        elif method == "inverse_distance":
            self.interploation = InverseDistance(parameter_h5_file, weight_name, radius)
        elif method == "linear_triangle":
            self.interploation = LinearTriangle(parameter_h5_file, weight_name)
        elif method == "thiessen_polygon":
            self.interploation = LinearTriangle(parameter_h5_file, weight_name)
        else:
            logger.info(f"Interpolation method {method} is not valide. Use inverst distance method instead.")
            self.interploation = InverseDistance(parameter_h5_file, weight_name)

    def generate_weight_cell(self, mask_raster:Raster):
        self.interploation.write_weight(mask_raster, self.station_coordinates)

    def generate_weight_subarea(self, subarea_centroid_df:pd.DataFrame):
        self.interploation.write_weight_subbarea(subarea_centroid_df, self.station_coordinates)
    
