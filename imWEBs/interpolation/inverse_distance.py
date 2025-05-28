from whitebox_workflows import Raster, Vector
import numpy as np
import pandas as pd
import math
from .interpolation import Interpolation
from ..raster_extension import RasterExtension
from ..names import Names
import h5py
import logging
logger = logging.getLogger(__name__)


class InverseDistance(Interpolation):
    def __init__(self, parameter_h5_file:str, weight_name:str, radius:int) -> None:
        super().__init__(parameter_h5_file, weight_name)
        self.radius = radius
    
    def write_weight_subbarea(self, subarea_centroid_df:pd.DataFrame, station_coordinates:list):
        if subarea_centroid_df is None:
            raise ValueError("Subarea centroid are not available.")
        
        subarea_centroid_df = subarea_centroid_df.sort_values(by=Names.field_name_id)
        numShapes = len(station_coordinates)

        dist = np.zeros(numShapes)
        rowCount = len(subarea_centroid_df)

        row_number = 0
        total_row = 0

        chunk = np.zeros((rowCount if rowCount < Interpolation.CHUNK_SIZE else Interpolation.CHUNK_SIZE, numShapes), dtype=np.float32)

        for index, row in subarea_centroid_df.iterrows():
            raster_x = row['x']
            raster_y = row['y']
            
            #calculate the distance
            found_station = False
            for i in range(numShapes):
                dist[i] = math.sqrt(math.pow(station_coordinates[i][0] - raster_x, 2) +
                                    math.pow(station_coordinates[i][1] - raster_y, 2))
                
                if dist[i] < self.radius:
                    found_station = True

            if not found_station:
                raise ValueError(f"There is no climate station in defined radius: {self.radius} m")

            #calculate the weights
            weights = self.normalize_weight(dist)

            #save to the chunk
            chunk[row_number:] = weights

            #append to file
            row_number = row_number + 1
            total_row = total_row + 1
            if row_number >= Interpolation.CHUNK_SIZE:
                logger.info(f"      -- {total_row}")
                with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                    if total_row <= Interpolation.CHUNK_SIZE:                            
                        h5_file.create_dataset(self.path, data = chunk,maxshape=(None, numShapes), chunks=True)
                    else:
                        h5_file[self.path].resize((total_row, numShapes))
                        h5_file[self.path][total_row - Interpolation.CHUNK_SIZE:] = chunk
                row_number = 0

        if row_number > 0:
            logger.info(f"      -- {total_row}")
            chunk = chunk[:row_number]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= Interpolation.CHUNK_SIZE:                
                    h5_file.create_dataset(self.path, data = chunk)
                else:
                    h5_file[self.path].resize((total_row, numShapes))
                    h5_file[self.path][total_row - row_number:] = chunk

    def write_weight(self, mask_raster:Raster, station_coordinates:list):
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)

        dist = np.zeros(numShapes)
        rowCount = RasterExtension.get_number_of_valid_cell(mask_raster)
        no_data = mask_raster.configs.nodata

        row_number = 0
        total_row = 0

        chunk = np.zeros((rowCount if rowCount < Interpolation.CHUNK_SIZE else Interpolation.CHUNK_SIZE, numShapes), dtype=np.float32)

        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != no_data:
                    raster_x = mask_raster.get_x_from_column(col)
                    raster_y = mask_raster.get_y_from_row(row)
                    
                    #calculate the distance
                    found_station = False
                    for i in range(numShapes):
                        dist[i] = math.sqrt(math.pow(station_coordinates[i][0] - raster_x, 2) +
                                            math.pow(station_coordinates[i][1] - raster_y, 2))
                        
                        if dist[i] < self.radius:
                            found_station = True

                    if not found_station:
                        raise ValueError(f"There is no climate station in defined radius: {self.radius} m")

                    #calculate the weights
                    weights = self.normalize_weight(dist)

                    #save to the chunk
                    chunk[row_number:] = weights

                    #append to file
                    row_number = row_number + 1
                    total_row = total_row + 1
                    if row_number >= Interpolation.CHUNK_SIZE:
                        logger.info(f"      -- {total_row}")
                        with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                            if total_row <= Interpolation.CHUNK_SIZE:                            
                                h5_file.create_dataset(self.path, data = chunk,maxshape=(None, numShapes), chunks=True)
                            else:
                                h5_file[self.path].resize((total_row, numShapes))
                                h5_file[self.path][total_row - Interpolation.CHUNK_SIZE:] = chunk
                        row_number = 0

        if row_number > 0:
            logger.info(f"      -- {total_row}")
            chunk = chunk[:row_number]
            with h5py.File(self.parameter_h5_file, 'a') as h5_file:
                if total_row <= Interpolation.CHUNK_SIZE:                
                    h5_file.create_dataset(self.path, data = chunk)
                else:
                    h5_file[self.path].resize((total_row, numShapes))
                    h5_file[self.path][total_row - row_number:] = chunk

    def normalize_weight(self, distance:list):
        #only use distance that is in the raidus
        dist = []
        dist_index = []
        for i in range(len(distance)):
            if distance[i] < self.radius:
                dist.append(distance[i])
                dist_index.append(i)

        tempDenom = 0
        aValuesIntSum = 0
        numShapes = len(dist)
        aValues = np.zeros(numShapes)
        aValuesInt = np.zeros(numShapes)

        for i in range(numShapes):
            tempDenom += 1 / math.pow(dist[i], 2)

        for i in range(numShapes):
            tempNum = 1 / math.pow(dist[i], 2)
            aValues[i] = tempNum / tempDenom
            aValuesInt[i] = math.floor(aValues[i] * 10000)

        while aValuesIntSum != 10000:
            aValuesIntSum = 0
            for i in range(numShapes):
                aValuesIntSum += aValuesInt[i]

            if aValuesIntSum > 10000:
                tempNums = [aValues[i] * 10000 - math.floor(aValues[i] * 10000) for i in range(numShapes)]
                for i in range(numShapes):
                    if tempNums[i] < 0.5:
                        tempNums[i] = 1

                for i in range(numShapes):
                    if tempNums[i] != 1:
                        lowestValue = True
                        for k in range(numShapes):
                            if tempNums[i] <= tempNums[k]:
                                lowestValue = True
                            else:
                                lowestValue = False
                                break

                        if lowestValue:
                            aValuesInt[i] = aValuesInt[i] - 1
                            aValues[i] = aValues[i] - 0.0001
                            break
            elif aValuesIntSum < 10000:
                tempNums = [aValues[i] * 10000 - math.floor(aValues[i] * 10000) for i in range(numShapes)]
                for i in range(numShapes):
                    if tempNums[i] > 0.5:
                        tempNums[i] = 0

                for i in range(numShapes):
                    if tempNums[i] != 1:
                        highestValue = True
                        for k in range(numShapes):
                            if tempNums[i] >= tempNums[k]:
                                highestValue = True
                            else:
                                highestValue = False
                                break

                        if highestValue:
                            aValuesInt[i] = aValuesInt[i] + 1
                            aValues[i] = aValues[i] + 0.0001
                            break

            aValuesIntSum = 0
            for i in range(numShapes):
                aValuesIntSum += aValuesInt[i]

        for i in range(numShapes):
            aValues[i] = aValuesInt[i] / 10000

        weights = np.zeros(len(distance))
        for i in range(numShapes):
            weights[dist_index[i]] = aValues[i]

        return weights
