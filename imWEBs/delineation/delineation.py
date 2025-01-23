from whitebox_workflows import WbEnvironment, Raster, RasterDataType, Vector
import numpy as np
import math
from datetime import datetime

class Delineation:   
    def __init__(self):
        pass

    # def getRasterCellAreaM2(raster:Raster):
    #     """Calculate the cell area in km2 assuming the resolution is in m"""
    #     #return raster.configs.resolution_x * raster.configs.resolution_y
    #     pass

    # def getRasterCellAreaKM2(raster:Raster):
    #     """Calculate the cell area in km2 assuming the resolution is in m"""
    #     #return getRasterCellAreaM2(raster) / 1e6
        

    # def calculateStreamDimension(flowAcc:Raster, mask:Raster, parameterA: float, parameterB: float) -> Raster:
    #     """
        
    #     Calculate Stream Width/Depth as (FlowAcc * Cell Area * A)^B. Width and depth will be calculated using different parameters. 
        
    #     Parameters:
    #     flowAcc         : Flow Accumualation Raster
    #     mask            : Stream Network Raster
    #     parameterA   : A
    #     parameterB   : B
        
    #     """

    #     return (flowAcc * getRasterCellArea(mask) * parameterA) ** parameterB

    # def lookupValues(inputRaster:Raster, mask: Raster, lookup:dict) -> Raster:
    #     """
    #     Replace the raster values based on lookup table. The application could be

    #     1. generate field capacity raster based on soil lookup table
    #     2. generate manning raster based on landuse lookup table
    #     3. 
        
    #     Parameters:
    #     inputRaster         : the input raster
    #     mask                : mask raster
    #     lookup              : lookup table assuming the input value is the key and output value is the value   
    #     """

    #     pass

    # def getSlopeRadius(slopeDeg:Raster)->Raster:
    #     return (slopeDeg * math.pi / 180).tan()

    # def calculateReachVelocity(manning:Raster, slopeRadius:Raster, streamDepth:Raster, mask:Raster, min:float = 0.005, max: float = 3) -> Raster:
    #     """
    #     Calculate full reach velocity using Manning equation

    #     Parameters:
    #     manning             : Manning raster
    #     slopeDeg            : Slope raster in degree. Could use radius instead
    #     streamDepth         : Stream depth raster
    #     mask                : mask raster
    #     min                 : min velocity
    #     max                 : max velocity

    #     """
    #     velocity = slopeRadius.sqrt() * streamDepth**0.6667 / manning
    #     return velocity.min(max).max(min)

    # def calculateWetnessIndex(flowAcc:Raster, slopeRadius:Raster, mask:Raster)->Raster:
    #     """
    #     Calculate wetness index using flow accumulation and slope
    #     """

    #     return (flowAcc * getRasterCellAreaM2(mask)).log() / slopeRadius.tan()

    # def calculateIntialSoilMoisture(wetnessIndex:Raster, fieldCapacity:Raster, mask:Raster, minSaturation:float=0.05, maxSaturation:float=1)->Raster:
    #     """
    #     Calculate the initial soil moisture using linear interpolation
    #     """

    #     minWetnessIndex = wetnessIndex.configs.minimum
    #     maxWetnessIndex = wetnessIndex.configs.maximum * 0.8

    #     wti = wetnessIndex.max(maxWetnessIndex)
    #     ratio = (wti - minWetnessIndex) * (maxSaturation - minSaturation) / (maxWetnessIndex - minWetnessIndex) + minSaturation
    #     return ratio * fieldCapacity
    
    def Raise_watershed(watershed_raster:Raster):
        """
        Raise the height of the watershed's extent
        """
        return watershed_raster.con("value > 0", watershed_raster + 200, watershed_raster.configs.nodata)

    def ValueAccumD8(self, d8_ras_file, value_ras_file,output_ras_file, is_average):
        row, col, x, y = 0, 0, 0, 0
        z, z2 = 0.0, 0.0
        v, v2 = 0.0, 0.0
        i = 0
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        inflowingVals = [16, 32, 64, 128, 1, 2, 4, 8]
        numInNeighbours = 0.0
        isAvg = False
        flag = False
        flowDir = 0.0

        isAvg = is_average

        try:
            wbe = WbEnvironment()

            pntr = wbe.read_raster(d8_ras_file)
            valueRas = wbe.read_raster(value_ras_file)

            noData = pntr.configs.nodata
            rows = pntr.configs.rows
            cols = pntr.configs.columns
            rowsLessOne = rows - 1
    
            output = wbe.new_raster(pntr.configs)
            temp = np.full((rows, cols), 1.0)

            tmpGrid1 = wbe.new_raster(pntr.configs)

            for row in range(rows):
                for col in range(cols):
                    if pntr[row, col] != noData and valueRas[row, col] != noData:
                        z = 0
                        for i in range(8):
                            if pntr[row + dY[i], col + dX[i]] == inflowingVals[i]:
                                z += 1
                        tmpGrid1[row, col] = z
                        output[row, col] = valueRas[row, col]
                    else:
                        temp[row, col] = noData

            for row in range(rows):
                for col in range(cols):
                    if tmpGrid1[row, col] == 0:
                        tmpGrid1[row, col] = -1
                        x, y = col, row
                        while True:
                            z = temp[y, x]
                            v = output[y, x]
                            flowDir = pntr[y, x]
                            if flowDir > 0:
                                i = int(math.log(flowDir) / math.log(2))
                                x += dX[i]
                                y += dY[i]
                                z2 = temp[y, x]
                                temp[y, x] = z2 + z
                                v2 = output[y, x]
                                output[y, x] = v2 + v
                                numInNeighbours = tmpGrid1[y, x] - 1
                                tmpGrid1[y, x] = numInNeighbours
                                if numInNeighbours == 0:
                                    tmpGrid1[y, x] = -1
                                    flag = True
                                else:
                                    flag = False
                            else:
                                flag = False
                            if not flag:
                                break

            if isAvg:
                for row in range(rows):
                    for col in range(cols):
                        flowDir = output[row, col]
                        if flowDir != noData and valueRas[row, col] != noData:
                            output[row, col] = output[row, col] / temp[row, col]
                        else:
                            output[row, col] = noData

            #save here
            wbe.write_raster(output, output_ras_file)

        except MemoryError:
            print("memory error")
        except Exception as e:
            print(e)
        finally:
            pass

    @staticmethod
    def get_flow_path_length(flow_dir_raster:Raster, dem_raster:Raster)->Raster:       
        """
        Replace plugin MaxUpslopeFlowpathLength
        """

        row, col, x, y = 0, 0, 0, 0
        z = 0.0
        currentVal = 0.0
        i = 0
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        inflowingVals = [16, 32, 64, 128, 1, 2, 4, 8]
        LnOf2 = 0.693147180559945
        numInNeighbours = 0.0
        flag = False
        flowDir = 0.0
        flowLength = 0.0
        
        
        rows = flow_dir_raster.configs.rows
        cols = flow_dir_raster.configs.columns
        noData = flow_dir_raster.configs.nodata
        gridResX = flow_dir_raster.configs.resolution_x
        gridResY = flow_dir_raster.configs.resolution_y

        diagGridRes = np.sqrt(gridResX * gridResX + gridResY * gridResY)
        gridLengths = [diagGridRes, gridResX, diagGridRes, gridResY, diagGridRes, gridResX, diagGridRes, gridResY]

        wbe = WbEnvironment()  
        flow_length_raster = wbe.new_raster(dem_raster.configs)
        for row in range(rows):
            for col in range(cols):
                flow_length_raster[row, col] = 0
        temp_raster = wbe.new_raster(dem_raster.configs)
        
        for row in range(rows):
            for col in range(cols):
                if flow_dir_raster[row, col] != noData:
                    z = 0
                    for i in range(8):
                        if flow_dir_raster[row + dY[i], col + dX[i]] == inflowingVals[i]:
                            z += 1
                    temp_raster[row, col] = z
                else:
                    flow_length_raster[row, col] = noData

        for row in range(rows):
            for col in range(cols):
                if temp_raster[row, col] == 0:
                    temp_raster[row, col] = -1
                    flag = False
                    x = col
                    y = row
                    while True:
                        flowLength = flow_length_raster[y, x]
                        flowDir = flow_dir_raster[y, x]
                        if flowDir > 0:
                            i = int(np.log(flowDir) / LnOf2)
                            flowLength += gridLengths[i]
                            x += dX[i]
                            y += dY[i]
                            
                            currentVal = flow_length_raster[y, x]
                            if flowLength > currentVal:
                                flow_length_raster[y, x] = flowLength
                            
                            numInNeighbours = temp_raster[y, x] - 1
                            temp_raster[y, x] = numInNeighbours
                            
                            if numInNeighbours == 0:
                                temp_raster[y, x] = -1
                                flag = True
                            else:
                                flag = False
                        else:
                            flag = False
                        if not flag:
                            break
        
        return flow_length_raster

    @staticmethod
    def generate_subbasin(flow_dir_raster:Raster, outlet_raster:Raster)->Raster:
        """
        The WhiteBox watershed plugin. 
        Just for testing purpose as the subbasin generated by WhiteBox version is slightly different than the one geneted with the worflow version.
        """
        row, col, x, y = 0, 0, 0, 0
        z = 0
        i, c = 0, 0
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        flag = False
        flowDir = 0
        outletID = 0

        wbe = WbEnvironment()
        LnOf2 = 0.693147180559945
        rows = flow_dir_raster.configs.rows
        cols = flow_dir_raster.configs.columns
        flow_dir_nodata = flow_dir_raster.configs.nodata
        outlet_nodata = outlet_raster.configs.nodata
        subbasin_raster = wbe.new_raster(outlet_raster.configs)
        subbasin_nodata = subbasin_raster.configs.nodata

        #output = np.full_like(pntr, -999)

        for row in range(rows):
            for col in range(cols):
                z = outlet_raster[row, col]
                if z != 0 and z != outlet_nodata:
                    subbasin_raster[row, col] = z

        for row in range(rows):
            for col in range(cols):
                if subbasin_raster[row, col] == subbasin_nodata and outlet_raster[row, col] != subbasin_nodata:
                    flag = False
                    x = col
                    y = row
                    while not flag:
                        flowDir = flow_dir_raster[y, x]
                        if flowDir > 0:
                            c = int(np.log(flowDir) / LnOf2)
                            x += dX[c]
                            y += dY[c]
                            z = subbasin_raster[y, x]
                            if z != subbasin_nodata:
                                outletID = z
                                flag = True
                        else:
                            outletID = subbasin_nodata
                            flag = True

                    flag = False
                    x = col
                    y = row
                    subbasin_raster[y, x] = outletID
                    while not flag:
                        flowDir = flow_dir_nodata[y, x]
                        if flowDir > 0:
                            c = int(np.log(flowDir) / LnOf2)
                            x += dX[c]
                            y += dY[c]
                            z = subbasin_raster[y, x]
                            if z != subbasin_nodata:
                                flag = True
                        else:
                            flag = True
                        subbasin_raster[y, x] = outletID
                elif flow_dir_raster[row, col] != flow_dir_nodata:
                    subbasin_raster[row, col] = subbasin_nodata
 
        return subbasin_raster


    @staticmethod
    def get_pour_points(stream_network_raster:Raster, flow_dir_raster:Raster, structure_rasters:list)->Vector:
        """
        * This method generate the pour points of the stream with the option of
        * setting exception areas, where pour points will be removed.
        *
        * @param streamHeader Input stream raster file. All cells pouring to the
        * same stream cell will be classify as a pour point
        * @param flowDirHeader Flow direction raster file path. This file will be
        * used to tracking the flow direction of the stream and find the pour
        * points
        * @param outputHeader Pour point raster file path (Output file).
        * @param exceptionAreas Array of exception areas (Optional). All pour
        * points within these areas will be removed

        This was used when uer click the watershed outlet button to provide user a list of outlets for selection. 
        This will not be used assuming provides the outlets in a shapefile. 

        Replace buildPourPoints
        """

        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        inflowing_vals = [16, 32, 64, 128, 1, 2, 4, 8]

        rows = flow_dir_raster.configs.rows
        cols = flow_dir_raster.configs.columns
        no_data = flow_dir_raster.configs.nodata
        has_exception = len(structure_rasters) > 0

        wbe = WbEnvironment()
        configs = flow_dir_raster.configs
        configs.data_type = RasterDataType.F32
        stream_outlets_raster = wbe.new_raster(configs)

        count = 0
        for row in range(rows):
            for col in range(cols):
                if stream_network_raster[row, col] > 0:
                    flow_dir = flow_dir_raster[row, col]
                    if flow_dir == 0:  # End of stream network
                        count += 1
                        stream_outlets_raster[row, col] = count
                        break

                    # Check if it is a headwater location
                    num_neighbouring_stream_cells = 0
                    for c in range(8):
                        x = col + dX[c]
                        y = row + dY[c]
                        if stream_network_raster[y, x] > 0 and flow_dir_raster[y, x] == inflowing_vals[c]:
                            num_neighbouring_stream_cells += 1

                    if num_neighbouring_stream_cells > 1:
                        if has_exception:
                            flag = True
                            for exception in structure_rasters:
                                if exception[row, col] > 0:
                                    flag = False
                                    break
                            if not flag:
                                break

                        for c in range(8):
                            x = col + dX[c]
                            y = row + dY[c]
                            if stream_network_raster[y, x] > 0 and flow_dir_raster[y, x] == inflowing_vals[c]:
                                if has_exception:
                                    flag = True
                                    for exception in structure_rasters:
                                        if exception[y, x] > 0:
                                            flag = False
                                            break
                                    if not flag:
                                        break

                                count += 1
                                stream_outlets_raster[y, x] = count

        return wbe.raster_to_vector_points(stream_outlets_raster)

    @staticmethod
    def build_stream_network_link_to_outlets(stream_network_raster:Raster, flow_dir_raster:Raster, outlets_raster:Raster)->Raster:
        """
        it basically add small stream that connects to outlets

        replace buildStreamNetworkLink2Outlets
        """
        #dX = [1, 1, 1, 0, -1, -1, -1, 0]
        #dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        #dmove = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
        dmove_dic = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)}  

        wbe = WbEnvironment()
        rows = stream_network_raster.configs.rows
        cols = stream_network_raster.configs.columns
        no_data = stream_network_raster.configs.nodata

        stream_network_modified_raster = wbe.new_raster(stream_network_raster.configs)
        flag_raster = wbe.new_raster(stream_network_raster.configs)

        for row in range(rows):
            for col in range(cols):
                #skip if the cell is already handled
                if flag_raster[row, col] > 0:
                    continue

                if stream_network_raster[row, col] > 0:
                    stream_network_modified_raster[row, col] = stream_network_raster[row, col]
                    flag_raster[row, col] = 1
                elif outlets_raster[row, col] > 0:
                    if flow_dir_raster[row, col] < 0:
                        break

                    x = col
                    y = row
                    value = no_data

                    path = []
                    path.append((x,y))
                    while value < 0:
                        flow_dir = flow_dir_raster[y, x]
                        if flow_dir > 0:
                            mv = dmove_dic[flow_dir]

                            x += mv[1]
                            y += mv[0]
                            value = stream_network_raster[y, x]
                            path.append((x,y))
                        else:
                            break

                    if value < 0:
                        value = 1

                    for point in path:
                        stream_network_modified_raster[point[1],point[0]] = value
                        flag_raster[point[1],point[0]] = 1

        return stream_network_modified_raster

    @staticmethod
    def reorder_raster_id(raster:Raster)->dict[int, int]:
        """
        it will modify the raster

        replace reorderRasterID
        """

        rows = raster.configs.rows
        cols = raster.configs.columns

        count = 0
        id_map = {}
        for row in range(rows):
            for col in range(cols):
                id = int(raster[row, col])
                if id > 0:
                    if id not in id_map:
                        count += 1
                        id_map[id] = count
                    raster[row, col] = id_map[id]

        return id_map

    @staticmethod
    def create_parts_drainage_area_raster(structure_raster:Raster, flow_direction_raster:Raster, subbasin_raster:Raster, create_new_id:bool = False)->tuple[Raster,Raster]:
        """
        Borrow from VFSandRBS
        """
        row, col, x, y = 0, 0, 0, 0
        z = 0.0
        i, c = 0, 0
        flag = False
        flowDir = 0.0

        if structure_raster is None:
            return None
        
        wbe = WbEnvironment()


        rows = flow_direction_raster.configs.rows
        cols = flow_direction_raster.configs.columns
        structure_nodata = structure_raster.configs.nodata
        subbasin_nodata = subbasin_raster.configs.nodata

        drainage_area_raster = wbe.new_raster(subbasin_raster.configs)
        parts_raster = wbe.new_raster(subbasin_raster.configs)

        #flag if the cells has been traced
        flag2D = np.zeros((rows, cols), dtype=bool)


        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        LnOf2 = 0.693147180559945
        path = []
        pathInside = []
        vfsOrRbsDrain = {}
        vfsOrRbsInside = {}
        vfsOrRbsLength = {}
        celldist = (structure_raster.configs.resolution_x + structure_raster.configs.resolution_y) / 2.0

        for row in range(rows):
            for col in range(cols):
                if subbasin_raster[row, col] != subbasin_nodata and not flag2D[row, col]:
                    path = []
                    pathInside = []

                    x = col
                    y = row

                    path.append((y, x))

                    flag = True
                    length = 0.0

                    while flag:
                        flowDir = flow_direction_raster[y, x]
                        if flowDir > 0:
                            c = int(math.log(flowDir) / LnOf2)

                            lastVFSorRBSID = structure_raster[y, x]
                            isVisited = flag2D[y, x]

                            if lastVFSorRBSID != structure_nodata and not isVisited:
                                pathInside.append((y, x))
                                length += celldist * (1.41421356 if c in [1, 4, 16, 64] else 1)

                            #get x,y for downstream cell
                            x += dX[c]
                            y += dY[c]

                            #check to see if the next cell is edge, different riparian buffer. If yes, add it to the list
                            if (structure_raster[y, x] == structure_nodata 
                                or structure_raster[y, x] != lastVFSorRBSID 
                                or flow_direction_raster[y, x] == 0) and lastVFSorRBSID != structure_nodata:
                                #recalculate the current position
                                loc = (y - dY[c], x - dX[c])

                                if loc in vfsOrRbsDrain:
                                    vfsOrRbsDrain[loc].extend(path)
                                else:
                                    vfsOrRbsDrain[loc] = path.copy()

                                if loc in vfsOrRbsInside:
                                    vfsOrRbsInside[loc].extend(pathInside)
                                else:
                                    vfsOrRbsInside[loc] = pathInside.copy()

                                if loc in vfsOrRbsLength:
                                    vfsOrRbsLength[loc] = max(length, vfsOrRbsLength[loc])
                                else:
                                    vfsOrRbsLength[loc] = length
                                break

                            if not isVisited:
                                path.append((y, x))
                        else:
                            flag = False

                    #update the flag
                    for loc in path:
                        flag2D[loc[0], loc[1]] = True

        new_id = 0
        for outLoc in vfsOrRbsDrain.keys():
            new_id += 1
            structure_id = int(structure_raster[outLoc[0], outLoc[1]])

            for loc in vfsOrRbsDrain[outLoc]:
                drainage_area_raster[loc[0], loc[1]] = new_id if create_new_id else structure_id

            for loc in vfsOrRbsInside[outLoc]:
                parts_raster[loc[0], loc[1]] = new_id if create_new_id else structure_id

        return (parts_raster, drainage_area_raster)

