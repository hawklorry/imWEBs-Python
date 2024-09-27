from whitebox_workflows import Raster

class Interpolation:
    def __init__(self, weight_file:str) -> None:
        self.weight_file = weight_file

    def write_weight_file(self, mask_raster:Raster, station_coordinates:list):
        """write weight file"""
        pass