from whitebox_workflows import Raster
import numpy as np
import math
from .interpolation import Interpolation
from ..raster_extension import RasterExtension

class InverseDistance(Interpolation):
    def __init__(self, weight_file: str, radius:int) -> None:
        super().__init__(weight_file)
        self.radius = radius
    
    def write_weight_file(self, mask_raster:Raster, station_coordinates:list):
        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)

        dist = np.zeros(numShapes)
        rowCount = RasterExtension.get_number_of_valid_cell(mask_raster)
        no_data = mask_raster.configs.nodata

        sb = []
        sb.append(str(rowCount))
        sb.append("\n")
        sb.append(str(numShapes))
        sb.append("\n")

        with open(self.weight_file, 'w') as out:
            out.write(''.join(sb))

        sb = []
        max_row = 100
        row_number = 1
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

                    #write to buffer
                    finalValue = str(weights[0])
                    for i in range(1, numShapes):
                        finalValue += "\t" + str(weights[i])

                    sb.append(finalValue)
                    sb.append("\n")

                    #flush to file
                    row_number = row_number + 1
                    if row_number > max_row:
                        with open(self.weight_file, 'a') as out:
                            out.write(''.join(sb))
                        sb = []
                        row_number = 1

        if len(sb) > 0:
            with open(self.weight_file, 'a') as out:
                out.write(''.join(sb))


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
