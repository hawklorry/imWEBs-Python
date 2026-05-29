import os
import math
import numpy as np
import pandas as pd
from .interpolation import Interpolation
from whitebox_workflows import Raster
from ..raster_extension import RasterExtension

class GridInterpolation(Interpolation):
    def __init__(self, parameter_h5_file:str, weight_name:str) -> None:
        super().__init__(parameter_h5_file, weight_name)

    def write_weight(self, mask_raster:Raster, station_coordinates:list):
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)
        rowCount = RasterExtension.get_number_of_valid_cell(mask_raster)
        no_data = mask_raster.configs.nodata

        if numShapes <= 2:
            raise ValueError("Grid Interpolation need at least three stations. ")

        sb = []
        sep = os.linesep
        sb.append(str(rowCount))
        sb.append(sep)
        sb.append(str(numShapes))
        sb.append(sep)

        xMax = mask_raster.get_x_from_column(0)
        xMin = xMax
        yMax = mask_raster.get_y_from_row(0)
        yMin = yMax

        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != no_data:
                    xMax = max(xMax, mask_raster[row, col])
                    xMin = min(xMin, mask_raster[row, col])
                    yMax = max(yMax, mask_raster[row, col])
                    yMin = min(yMin, mask_raster[row, col])

        dist = np.zeros(numShapes)
        minDist = np.zeros(5)
        minDistStationNum = np.zeros(5, dtype=int)
        quadrant = np.zeros(numShapes, dtype=int)
        zeroes = 0
        count = np.zeros(5, dtype=int)
        finalValue = np.empty((rows, cols), dtype=object)

        for i in range(5):
            count[i] = 0
            minDist[i] = 0

        for i in range(numShapes):
            x = station_coordinates[i][0]
            y = station_coordinates[i][1]
        
            if x > xMax and y > yMax:
                quadrant[i] = 1
                count[1] += 1
            elif x > xMax and y < yMin:
                quadrant[i] = 2
                count[2] += 1
            elif x < xMin and y < yMin:
                quadrant[i] = 3
                count[3] += 1
            elif x < xMin and y > yMax:
                quadrant[i] = 4
                count[4] += 1
            else:
                quadrant[i] = 4
                count[0] += 1

        zeroes = sum(1 for i in range(1, 5) if count[i] == 0)

        if zeroes > 1:
            raise ValueError("Grid interpolation not possible!")

        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != no_data:
                    raster_x = mask_raster.get_x_from_column(col)
                    raster_y = mask_raster.get_y_from_row(row)
                
                    for i in range(numShapes):
                        x = station_coordinates[i][0]
                        y = station_coordinates[i][1]
                        dist[i] = math.sqrt((x - raster_x) ** 2 + (y - raster_y) ** 2)

                    for i in range(numShapes):
                        for k in range(1, 5):
                            if count[k] != 0:
                                if quadrant[i] == k:
                                    if minDist[k] == 0:
                                        minDist[k] = dist[i]
                                    else:
                                        if minDist[k] > dist[i]:
                                            minDist[k] = dist[i]
                                            minDistStationNum[k] = i

                    radius = np.ones(5)
                    multiplier = np.zeros(5, dtype=int)
                    for i in range(1, 5):
                        if count[i] == 0:
                            radius[i] = 1
                            multiplier[i] = 0
                        else:
                            radius[i] = minDist[i]
                            multiplier[i] = 1

                    cValue = (multiplier[4] * (radius[1] * radius[2] * radius[3]) ** 2 +
                                multiplier[1] * (radius[2] * radius[3] * radius[4]) ** 2 +
                                multiplier[3] * (radius[1] * radius[2] * radius[4]) ** 2 +
                                multiplier[2] * (radius[1] * radius[3] * radius[4]) ** 2)

                    cValues = np.zeros(5)
                    cValuesInt = np.zeros(5, dtype=int)
                    cValues[1] = multiplier[1] * ((radius[2] * radius[3] * radius[4]) ** 2) / cValue
                    cValues[2] = multiplier[2] * ((radius[1] * radius[3] * radius[4]) ** 2) / cValue
                    cValues[3] = multiplier[3] * ((radius[1] * radius[2] * radius[4]) ** 2) / cValue
                    cValues[4] = multiplier[4] * ((radius[1] * radius[2] * radius[3]) ** 2) / cValue

                    for i in range(1, 5):
                        if count[i] == 0:
                            cValues[i] = 0
                        cValuesInt[i] = int(cValues[i] * 10000)

                    cValueIntSum = cValuesInt[1] + cValuesInt[2] + cValuesInt[3] + cValuesInt[4]
                    tempNums = np.zeros(5)

                    if cValueIntSum > 10000:
                        for i in range(1, 5):
                            tempNums[i] = cValues[i] * 10000 - math.floor(cValues[i] * 10000)
                            if tempNums[i] < 0.5:
                                tempNums[i] = 1

                        for i in range(1, 5):
                            if tempNums[i] != 0:
                                if tempNums[i] <= tempNums[1] and tempNums[i] <= tempNums[2] and tempNums[i] <= tempNums[3] and tempNums[i] <= tempNums[4]:
                                    cValuesInt[i] -= 1
                    elif cValueIntSum < 10000:
                        for i in range(1, 5):
                            tempNums[i] = cValues[i] * 10000 - math.floor(cValues[i] * 10000)
                            if tempNums[i] > 0.5:
                                tempNums[i] = 0

                        for i in range(1, 5):
                            if tempNums[i] != 0:
                                if tempNums[i] >= tempNums[1] and tempNums[i] >= tempNums[2] and tempNums[i] >= tempNums[3] and tempNums[i] >= tempNums[4]:
                                    cValuesInt[i] += 1

                    stationsNumberSst = np.zeros(5, dtype=int)
                    for i in range(1, 5):
                        stationsNumberSst[i] = minDistStationNum[i]

                    finalValues = np.zeros(numShapes, dtype=int)
                    for i in range(1, 5):
                        finalValues[stationsNumberSst[i]] = round(cValuesInt[i] / 10000)

                    finalValue[row, col] = str(finalValues[0])
                    for i in range(1, numShapes):
                        finalValue[row, col] += "\t" + str(finalValues[i])

                    sb.append(str(finalValue[row, col]))
                    sb.append(sep)

        with open(self.weight_file, 'w') as out:
            out.write(''.join(sb))



