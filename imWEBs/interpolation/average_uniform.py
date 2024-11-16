import os
import logging
from .interpolation import Interpolation
from whitebox_workflows import Raster
from ..raster_extension import RasterExtension

class AverageUniform(Interpolation):
    def __init__(self, weight_file: str) -> None:
        super().__init__(weight_file)

    def write_weight_file(self, mask_raster:Raster, station_coordinates:list):
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)
        rowCount = RasterExtension.get_number_of_valid_cell(mask_raster)

        sb = []
        sb.append(str(rowCount))
        sb.append(str(numShapes))

        if numShapes != 0:
            weight = 10000 // numShapes / 10000
            weightf = 1 - (weight * (numShapes - 1)) if weight * numShapes != 1 else weight

            for row in range(rows):
                for col in range(cols):
                    if mask_raster[row, col] > 0:
                        finalValue = str(weight)
                        if numShapes > 1:
                            finalValue += "\t" + "\t".join([str(weight)] * (numShapes - 1)) + "\t" + str(weightf)
                        sb.append(finalValue)

        with open(self.weight_file, 'w') as out:
            out.write("\n".join(sb))