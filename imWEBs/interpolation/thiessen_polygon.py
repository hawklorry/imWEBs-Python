import os
from .interpolation import Interpolation
from whitebox_workflows import Raster, WbEnvironment

class ThiessenPolygon(Interpolation):
    def __init__(self, weight_file: str) -> None:
        super().__init__(weight_file)    

    def write_weight_file(self, mask_raster:Raster, station_coordinates:list):    
        wbe = WbEnvironment()

        rows = mask_raster.configs.rows
        cols = mask_raster.configs.columns
        numShapes = len(station_coordinates)
        
        station_id_raster = wbe.new_raster(mask_raster.configs)
        
        dist = [0.0] * numShapes
        rowCount = 0
        
        for row in range(rows):
            for col in range(cols):
                if mask_raster[row, col] > 0:
                    raster_x = mask_raster.get_x_from_column(col)
                    raster_y = mask_raster.get_y_from_row(row)

                    dist[0] = ((station_coordinates[0][0] - raster_x) ** 2 + 
                                (station_coordinates[0][1] - raster_y) ** 2) ** 0.5
                    minDist = dist[0]
                    minDistId = 0
                    
                    for i in range(1, numShapes):
                        dist[i] = ((station_coordinates[i][0] - raster_x) ** 2 + 
                                    (station_coordinates[i][1] - raster_y) ** 2) ** 0.5
                        if dist[i] < minDist:
                            minDist = dist[i]
                            minDistId = i
                    
                    station_id_raster[row, col] = minDistId
        
        sb = []
        sep = os.linesep
        
        sb.append(str(rowCount))
        sb.append(sep)
        sb.append(str(numShapes))
        sb.append(sep)
        
        finalValues = [0] * numShapes
        
        for row in range(rows):
            for col in range(cols):
                currentValue = int(station_id_raster[row, col])
                finalValues = [0] * numShapes
                finalValues[currentValue] = 1
                finalValue = str(finalValues[0])
                for i in range(1, numShapes):
                    finalValue += "\t" + str(finalValues[i])
                
                sb.append(finalValue)
                sb.append(sep)
        
        with open(self.weight_file, 'w') as out:
            out.write(''.join(sb))

