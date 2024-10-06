from .interpolation import Interpolation
from .average_uniform import AverageUniform
from .grid_interpolation import GridInterpolation
from .inverse_distance import InverseDistance
from .linear_triangle import LinearTriangle
from .thiessen_polygon import ThiessenPolygon
from whitebox_workflows import Raster
import logging
logger = logging.getLogger(__name__)

def WriteWeightFile(method:str, weight_file:str,mask_raster:Raster, station_coordinates:list):
    #get interpolation object based on method
    interploation = Interpolation(weight_file)
    if method == "average_uniform":
        interploation = AverageUniform(weight_file)
    elif method == "grid_interpolation":
        interploation = GridInterpolation(weight_file)
    elif method == "inverse_distance":
        interploation = InverseDistance(weight_file)
    elif method == "linear_triangle":
        interploation = LinearTriangle(weight_file)
    elif method == "thiessen_polygon":
        interploation = LinearTriangle(weight_file)
    else:
        logger.info(f"Interpolation method {method} is not valide. Use inverst distance method instead.")
        interploation = InverseDistance(weight_file)

    #generate the file
    interploation.write_weight_file(mask_raster, station_coordinates)
    
