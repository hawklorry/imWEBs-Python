import os
from .interpolation import Interpolation
from whitebox_workflows import Raster, WbEnvironment
import numpy as np
from ..raster_extension import RasterExtension

class LinearTriangle(Interpolation):
    def __init__(self, weight_file: str) -> None:
        super().__init__(weight_file) 

    def write_weight_file(self, mask_raster:Raster, station_coordinates:list): 
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)
        rowCount = RasterExtension.get_number_of_valid_cell(mask_raster)
        no_data = mask_raster.configs.nodata

        sb = []
        sep = os.linesep
        sb.append(str(rowCount))
        sb.append(sep)
        sb.append(str(numShapes))
        sb.append(sep)

        if numShapes <= 2:
            raise ValueError("Linear Triangle need at least three stations. ")

        dist = np.zeros(numShapes)
        d123 = np.zeros(3)
        stationsNum = np.zeros(3, dtype=int)
        aValues = np.zeros(3)
        aValuesInt = np.zeros(3, dtype=int)
        x = np.zeros(3)
        y = np.zeros(3)

        finalValue = [[""] * cols for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] != no_data:
                    d123[:] = np.inf
                    stationsNum[:] = 0
                    x[:] = 0
                    y[:] = 0

                    raster_x = mask_raster.get_x_from_column(col)
                    raster_y = mask_raster.get_y_from_row(row)

                    x = station_coordinates[i][0]
                    y = station_coordinates[i][1]

                    for i in range(numShapes):
                        dist[i] = np.sqrt((station_coordinates[i][0] - raster_x) ** 2 +
                                            (station_coordinates[i][1] - raster_y) ** 2)

                        if dist[i] < d123[0]:
                            d123[2] = d123[1]
                            stationsNum[2] = stationsNum[1]
                            x[2] = x[1]
                            y[2] = y[1]

                            d123[1] = d123[0]
                            stationsNum[1] = stationsNum[0]
                            x[1] = x[0]
                            y[1] = y[0]

                            d123[0] = dist[i]
                            stationsNum[0] = i
                            x[0] = x
                            y[0] = y
                        elif dist[i] < d123[1]:
                            d123[2] = d123[1]
                            stationsNum[2] = stationsNum[1]
                            x[2] = x[1]
                            y[2] = y[1]

                            d123[1] = dist[i]
                            stationsNum[1] = i
                            x[1] = x
                            y[1] = y
                        elif dist[i] < d123[2]:
                            d123[2] = dist[i]
                            stationsNum[2] = i
                            x[2] = x
                            y[2] = y

                    sValues = np.zeros(3)
                    sValuesSum = 0
                    for i in range(3):
                        sValues[0] = abs(raster_x * y[1] +
                                        (raster_y * x[2]) +
                                        (x[1] * y[2]) - (y[1] * x[2]) -
                                        (raster_x * x[1]) -
                                        (raster_y * y[2]))
                        sValues[1] = abs((x[0] * raster_y) +
                                        (y[0] * x[2]) +
                                        (raster_x * y[2]) -
                                        (raster_y * x[2]) -
                                        (y[0] * raster_x) -
                                        (x[0] * y[2]))
                        sValues[2] = abs((x[0] * y[1]) +
                                        (y[0] * raster_x) +
                                        (x[1] * raster_y) -
                                        (y[1] * raster_x) -
                                        (y[0] * x[1]) -
                                        (x[0] * raster_y))
                        sValues[0] = abs(sValues[0])
                        sValues[1] = abs(sValues[1])
                        sValues[2] = abs(sValues[2])
                        sValuesSum = sValues[0] + sValues[1] + sValues[2]

                    aValuesIntSum = 0

                    for i in range(3):
                        aValues[i] = sValues[i] / sValuesSum
                        aValuesInt[i] = int(aValues[i] * 10000)
                        aValuesIntSum += aValuesInt[i]

                    if aValuesIntSum > 10000:
                        tempNums = np.zeros(3)
                        for i in range(3):
                            tempNums[i] = aValues[i] * 10000 - np.floor(aValues[i] * 10000)
                            if tempNums[i] < 0.5:
                                tempNums[i] = 1

                        for i in range(3):
                            if tempNums[i] != 1:
                                if tempNums[i] <= tempNums[0] and tempNums[i] <= tempNums[1] and tempNums[i] <= tempNums[2]:
                                    aValuesInt[i] = aValuesInt[i] - 1
                    elif aValuesIntSum < 10000:
                        tempNums = np.zeros(3)
                        for i in range(3):
                            tempNums[i] = aValues[i] * 10000 - np.floor(aValues[i] * 10000)
                            if tempNums[i] > 0.5:
                                tempNums[i] = 0

                        for i in range(3):
                            if tempNums[i] != 1:
                                if tempNums[i] >= tempNums[0] and tempNums[i] >= tempNums[1] and tempNums[i] >= tempNums[2]:
                                    aValuesInt[i] = aValuesInt[i] + 1

                    finalValues = np.zeros(numShapes, dtype=int)

                    for i in range(numShapes):
                        finalValues[i] = 0
                    for i in range(3):
                        finalValues[stationsNum[i]] = aValuesInt[i]

                    finalValue[row][col] = str(round(float(finalValues[0]) / 10000))
                    for i in range(1, numShapes):
                        finalValue[row][col] += "\t" + str(round(float(finalValues[i]) / 10000))

                    sb.append(str(finalValue[row][col]))
                    sb.append(sep)

        with open(self.weight_file, 'w') as out:
            out.write(''.join(sb))


