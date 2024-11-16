# %%
from whitebox_workflows import WbEnvironment, Raster, Vector
import numpy as np
import math
from operator import itemgetter, attrgetter

# %%
wbe = WbEnvironment()

# %%
class GridCell:
    def __init__(self, row: int, col: int, z: float, flatIndex: int, streamVal: bool = True):
        self.row = row
        self.col = col
        self.z = z
        self.flatIndex = flatIndex
        self.streamVal = streamVal

    def __lt__(self, other):
        if self.streamVal and not other.streamVal:
            return True
        elif not self.streamVal and other.streamVal:
            return False
        elif self.z > other.z:
            return True
        elif self.z < other.z:
            return False
        elif self.flatIndex > other.flatIndex:
            return True
        elif self.flatIndex < other.flatIndex:
            return False
        return False

LnOf2 = 0.693147180559945

def WetlandOutletsPFO(
        demFile:str, 
        wetlandRasFile:str, 
        outputFile: str, 
        isAllowMultiOutlet: bool = False, 
        isUsingPFO: bool = True, 
        pntrFile: str = ""):
    """
    Find Wetland Outlets with PFO

    Parameters
    ----------
    demFile             : DEM file path
    wetlandRasFile      : Wetland file path 
    outputFile          : the column name 
    isAllowMultiOutlet  : If multiple outlets are allowed
    isUsingPFO          : If PFO is used
    pntrFile            : The pointer file path

    """

    try:
        progress, oldProgress, col, row, colN, rowN = 0, 0, 0, 0, 0, 0
        numSolvedCells = 0
        n = 0
        z, zN = 0.0, 0.0
        isPit, isEdgeCell, isWetland, flag = False, False, False, False
        gc = None
        """
        * 7  8  1
        * 6  X  2
        * 5  4  3
        """
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        backLink = [5, 6, 7, 8, 1, 2, 3, 4]

        wetlandRas = wbe.read_raster(wetlandRasFile)

        # read the input image
        dem = wbe.read_raster(demFile)
        nodata = dem.configs.nodata
        rows = dem.configs.rows
        cols = dem.configs.columns


        dem2D = np.full((rows, cols), nodata)
        output = np.full((rows, cols), nodata)
        flowdir = np.full((rows, cols), 0, dtype = np.unsignedinteger) 
        queue = []
        inQueue = np.full((rows, cols), False, dtype = bool) 

        # initialize the grids
        oldProgress = -1
        flatIndex = 0
        k = 0
        dir = 0
        x, y = 0, 0
        if isUsingPFO:                
            #Loop through cells to find cells that are pit and edge
            for row in range(rows):
                for col in range(cols):
                    z = dem[row, col]
                    dem2D[row, col] = z
                    flowdir[row, col] = 0
                    if z != nodata:
                        isWetland = wetlandRas[row, col] > 0
                        isPit = True
                        isEdgeCell = False
                        for n in range(8):
                            zN = dem[row + dY[n], col + dX[n]]
                            if isPit and zN != nodata and zN < z:
                                isPit = False
                            elif zN == nodata:
                                isEdgeCell = True
                        if isPit and isEdgeCell:
                            queue.append(GridCell(row, col, z, 0))
                            inQueue[row, col] = True
                    else:
                        numSolvedCells += 1

            row = 0
            col = 0

            queue = sorted(queue, key=attrgetter('z'))
            queue = sorted(queue, key=attrgetter('flatIndex'))

            while len(queue) > 0:
                gc = queue.pop(0)
                row = gc.row
                col = gc.col
                flatIndex = gc.flatIndex

                for n in range(8):
                    rowN = row + dY[n]
                    colN = col + dX[n]
                    zN = dem2D[rowN, colN]
                    if zN != nodata and not inQueue[rowN, colN]:
                        numSolvedCells += 1
                        flowdir[rowN, colN] = backLink[n]
                        k = 0
                        if zN == dem2D[row, col]:
                            k = flatIndex + 1
                        queue.append(GridCell(rowN, colN, zN, k))

                        inQueue[rowN, colN] = True

                        if wetlandRas[row, col] != wetlandRas[rowN, colN]:
                            flag = True
                            x = colN
                            y = rowN
                            isReturn = False
                            while flag:
                                # find the downslope neighbour
                                dir = flowdir[y, x] - 1
                                if dir > 0:
                                    if dir > 7:
                                        return
                                    x += dX[dir]
                                    y += dY[dir]
                                    if wetlandRas[y, x] > 0:
                                        if wetlandRas[rowN, colN] == wetlandRas[y, x]:
                                            isReturn = True
                                            flag = False
                                        else:
                                            isReturn = False
                                            flag = False
                                else:
                                    flag = False
                            if not isReturn:
                                output[rowN, colN] = wetlandRas[rowN, colN]
        else:
            pntr = wbe.read_raster(pntrFile)
            c = 0
            for row in range(rows):
                for col in range(cols):
                    if pntr[row, col] > 0 and wetlandRas[row, col] > 0:
                        z = dem[row, col]
                        dem2D[row, col] = z
                        dir = int(pntr[row, col])
                        if dir > 0:
                            c = int(math.log(dir) / LnOf2)
                            if c > 7:
                                print("An unexpected value has "
                                             + "been identified in the pointer "
                                             + "image. This tool requires a "
                                             + "pointer grid that has been "
                                             + "created using either the D8 "
                                             + "or Rho8 tools.")
                                return

                            rowN = row + dX[c]
                            colN = col + dY[c]

                            if wetlandRas[row, col] != wetlandRas[rowN, colN]:
                                flag = True
                                x = colN
                                y = rowN
                                isReturn = False

                                count = 0
                                while flag and count < 100:
                                    # find the downslope neighbour
                                    dir = int(pntr[y, x])
                                    if dir > 0:
                                        c = int(math.log(dir) / LnOf2)
                                        if c > 7:
                                            print("An unexpected value has "
                                                         + "been identified in the pointer "
                                                         + "image. This tool requires a "
                                                         + "pointer grid that has been "
                                                         + "created using either the D8 "
                                                         + "or Rho8 tools.")
                                            return

                                        if wetlandRas[y, x] > 0:
                                            if wetlandRas[row, col] == wetlandRas[y, x]:
                                                isReturn = True
                                                flag = False
                                            else:
                                                isReturn = False
                                                flag = False
                                        x += dX[c]
                                        y += dY[c]
                                    else:
                                        flag = False
                                    count += 1
                                if not isReturn:
                                    output[row, col] = wetlandRas[row, col]

        # Group the outlets and use the lowest one as the outlet
        outputNew = np.full((rows, cols), nodata)
        if isAllowMultiOutlet:
            register = {}
            registerReverse = np.full((rows, cols), int(nodata), dtype=int)
            grpNum = 0
            for row in range(rows):
                for col in range(cols):
                    if output[row, col] > 0:
                        loc = [row, col]
                        num = -1
                        for n in range(8):
                            rowN = row + dY[n]
                            colN = col + dX[n]
                            if output[row, col] == output[rowN, colN]:
                                if registerReverse[rowN, colN] > 0:
                                    num = registerReverse[rowN, colN]
                                    break
                        if num < 0:
                            grpNum += 1
                            register[grpNum] = []
                            num = grpNum
                        registerReverse[row, col] = num
                        register[num].append(loc)

            elevMap = {}
            for lst in register.values():
                elevMap = {}
                for loc in lst:
                    elevMap[dem[loc[0], loc[1]]] = loc
                elev = list(elevMap.keys())
                elev.sort()
                lowest = elev[0]
                outputNew[elevMap[lowest][0], elevMap[lowest][1]] = output[elevMap[lowest][0], elevMap[lowest][1]]

            # For multiple outlets wetland, outlet flow to wetland will not be count
            wetlandOutlets = {}
            suspectCounts = {}
            suspects = []
            for row in range(rows):
                for col in range(cols):
                    if outputNew[row, col] > 0 and wetlandRas[row, col] > 0:
                        id = int(wetlandRas[row, col])
                        if id in wetlandOutlets:
                            wetlandOutlets[id] += 1
                        else:
                            wetlandOutlets[id] = 1

                        dir = flowdir[row, col] - 1
                        if dir > 0:
                            if dir > 7:
                                return

                            rowN = row + dX[dir]
                            colN = col + dY[dir]

                            if wetlandRas[rowN, colN] > 0:
                                loc = [row, col]
                                suspects.append(loc)
                                if id in suspectCounts:
                                    suspectCounts[id] += 1
                                else:
                                    suspectCounts[id] = 1

            for loc in suspects:
                id = int(wetlandRas[loc[0], loc[1]])
                if wetlandOutlets[id] > 1 and wetlandOutlets[id] > suspectCounts[id]:
                    outputNew[loc[0], loc[1]] = nodata
        else:
            register = {}
            for row in range(rows):
                for col in range(cols):
                    if output[row, col] > 0:
                        id = int(output[row, col])
                        loc = [row, col]
                        if id not in register:
                            register[id] = []
                        register[id].append(loc)

            elevMap = {}
            for lst in register.values():
                elevMap = {}
                for loc in lst:
                    elevMap[dem[loc[0], loc[1]]] = loc
                elev = list(elevMap.keys())
                elev.sort()
                lowest = elev[0]
                outputNew[elevMap[lowest][0], elevMap[lowest][1]] = output[elevMap[lowest][0], elevMap[lowest][1]]

        # output the data
        outputRaster = wbe.new_raster(dem.configs)        
        for row in range(rows):
            for col in range(cols):
                z = dem2D[row, col]
                if z != nodata:
                    outputRaster[row, col] = outputNew[row, col]

        wbe.write_raster(outputRaster, outputFile)

    except MemoryError as oe:
        pass
    except Exception as e:
        pass
    finally:
        pass

def WetlandDirection(dem_raster:Raster, boundary_vector:Vector, boundary_raster:Raster, outlet_raster:Raster, stream_raster:Raster,lowerThresholdArea, upperThresholdArea):
    int_progress, old_progress, col, row, colN, rowN, numSolvedCells = 0, 0, 0, 0, 0, 0, 0
    numPits, r, j = 0, 0, 0
    int_dir, n = 0, 0
    double_z, double_zN, double_zTest, double_zN2, double_lowestNeighbour = 0.0, 0.0, 0.0, 0.0, 0.0
    bool_isPit, bool_isEdgeCell, bool_isWetland, bool_flag = False, False, False, False
    GridCell gc
    double_LARGE_NUM = float('inf')
    int_numInflowing = 0
    double_s, double_sN = 0.0, 0.0
    int_dX = [1, 1, 1, 0, -1, -1, -1, 0]
    int_dY = [-1, 0, 1, 1, 1, 0, -1, -1]
    int_backLink = [5, 6, 7, 8, 1, 2, 3, 4]
    double_outPointer = [0, 1, 2, 4, 8, 16, 32, 64, 128]

    inflowingVals = [16, 32, 64, 128, 1, 2, 4, 8]
    pntr = None

    nodata = dem_raster.configs.nodata
    rows = dem_raster.configs.rows
    cols = dem_raster.configs.columns
    rowsLessOne = rows - 1
    colsLessOne = cols - 1
    numCellsTotal = rows * cols

    elevDigits = len(str(int(dem_raster.configs.maximum)))
    elevMultiplier = math.pow(10, 8 - elevDigits)
    SMALL_NUM = 1 / elevMultiplier * 10
    priority = 0

    wetlandID = np.full((rows, cols), -32768, dtype=int)
    wetlandPosition = np.full((rows, cols), -32768, dtype=int)
    wetlandEndNodes = np.zeros((rows, cols), dtype=bool)

    numFeatures = boundary_vector.num_records
    count = 0
    points = []
    startingPointInPart, endingPointInPart = 0, 0
    i = 0
    x1, y1, x2, y2 = 0, 0, 0, 0
    box = None
    topRow, bottomRow, leftCol, rightCol = 0, 0, 0, 0
    rowYCoord, colXCoord = 0.0, 0.0

    featureNum = 0
    oldProgress = -1
    conflictWetlands = set()
    usedRec = np.full((rows, cols), -32768, dtype=int)

    for record_index in range(boundary_vector.num_records):

        recNum = record.recordNumber
        points = record.geometry.points
        numPoints = len(points)
        partData = record.geometry.parts
        numParts = len(partData)

        for part in range(numParts):
            featureNum += 1
            startingPointInPart = partData[part]
            if part < numParts - 1:
                endingPointInPart = partData[part + 1]
            else:
                endingPointInPart = numPoints
            n = 0
            for i in range(startingPointInPart, endingPointInPart - 1):
                x1 = int(points[i][0])
                y1 = int(points[i][1])
                x2 = int(points[i + 1][0])
                y2 = int(points[i + 1][1])
                d = 0
                dy = abs(y2 - y1)
                dx = abs(x2 - x1)
                dy2 = dy * 2
                dx2 = dx * 2
                ix = 1 if x1 < x2 else -1
                iy = 1 if y1 < y2 else -1
                if dy <= dx:
                    while True:
                        if dem[y1, x1] != nodata:
                            if usedRec[y1, x1] > 0 and usedRec[y1, x1] != recNum:
                                wetID = int(wetlandRas[y1, x1])
                                if wetID not in conflictWetlands:
                                    conflictWetlands.add(wetID)
                                    for n in range(8):
                                        rowN = y1 + int_dY[n]
                                        colN = x1 + int_dX[n]
                                        neighbourID = int(wetlandRas[rowN, colN])
                                        if neighbourID > 0 and neighbourID != wetID:
                                            if neighbourID not in conflictWetlands:
                                                conflictWetlands.add(neighbourID)
                            else:
                                n += 1
                                usedRec[y1, x1] = recNum
                                wetlandPosition[y1, x1] = n
                            wetlandID[y1, x1] = featureNum
                        if x1 == x2:
                            break
                        x1 += ix
                        d += dy2
                        if d > dx:
                            y1 += iy
                            d -= dx2
                else:
                    while True:
                        if dem[y1, x1] != nodata:
                            if usedRec[y1, x1] > 0 and usedRec[y1, x1] != recNum:
                                wetID = int(wetlandRas[y1, x1])
                                if wetID not in conflictWetlands:
                                    conflictWetlands.add(wetID)
                                    for n in range(8):
                                        rowN = y1 + int_dY[n]
                                        colN = x1 + int_dX[n]
                                        neighbourID = int(wetlandRas[rowN, colN])
                                        if neighbourID > 0 and neighbourID != wetID:
                                            if neighbourID not in conflictWetlands:
                                                conflictWetlands.add(neighbourID)
                            else:
                                n += 1
                                usedRec[y1, x1] = recNum
                                wetlandPosition[y1, x1] = n
                            wetlandID[y1, x1] = featureNum
                        if y1 == y2:
                            break
                        y1 += iy
                        d += dx2
                        if d > dy:
                            x1 += ix
                            d -= dy2
            count += 1

    confWetGroups = defaultdict(list)
    confWetIsAdded = {id: -1 for id in conflictWetlands}

    riparianWetlandIDs = set()
    riparianWetlandRemoveIDs = set()
    stream = None
    if streamFile:
        stream = np.load(streamFile)
    else:
        print("No stream provided, no riparian wetland found!")

    wetlandCount = defaultdict(int)
    nodataWet = wetlandRas.fill_value
    counter = 0
    for row in range(rows):
        for col in range(cols):
            if wetlandID[row, col] == -32768 and dem[row, col] != nodata and wetlandRas[row, col] > 0:
                id = int(wetlandRas[row, col])
                wetlandPix = wetlandCount.get(id, 0)
                wetlandCount[id] = wetlandPix + 1
                wetlandID[row, col] = id
                if stream is not None and stream[row, col] > 0 and pntr is not None and pntr[row, col] > 0:
                    counter = 0
                    for n in range(8):
                        rowN = row + int_dY[n]
                        colN = col + int_dX[n]
                        if stream[rowN, colN] > 0 and pntr[rowN, colN] == inflowingVals[n]:
                            counter += 1
                    if counter < 1 and id not in riparianWetlandRemoveIDs:
                        riparianWetlandRemoveIDs.add(id)
                    if id not in riparianWetlandIDs and id not in riparianWetlandRemoveIDs:
                        riparianWetlandIDs.add(id)
                if id in conflictWetlands and confWetIsAdded[id] < 0:
                    grpNum = 0
                    while grpNum in confWetGroups:
                        grpNum += 1
                    confWetGroups[grpNum].append(id)
                    confWetIsAdded[id] = grpNum
                    for n in range(8):
                        rowN = row + int_dY[n]
                        colN = col + int_dX[n]
                        neighbourID = int(wetlandRas[rowN, colN])
                        if neighbourID > 0 and neighbourID != id and neighbourID in conflictWetlands:
                            for grp in confWetGroups.values():
                                if id in grp and neighbourID not in grp:
                                    grp.append(neighbourID)
                                    confWetIsAdded[neighbourID] = confWetIsAdded[id]

    biggestWet = set()
    for grpNum in confWetGroups:
        if len(confWetGroups[grpNum]) == 1:
            biggestWet.add(confWetGroups[grpNum][0])
            continue
        pix = 0
        test = 0
        for id in confWetGroups[grpNum]:
            try:
                if wetlandCount[id] > pix:
                    pix = wetlandCount[id]
                    if id in biggestWet:
                        biggestWet.remove(id)
                    test = id
            except Exception as e:
                print(id)
        if test > 0 and test not in biggestWet:
            biggestWet.add(test)

    for big in biggestWet:
        conflictWetlands.remove(big)

    for removeID in riparianWetlandRemoveIDs:
        if removeID in riparianWetlandIDs:
            riparianWetlandIDs.remove(removeID)

    pixelArea = dem.cellsize[0] * dem.cellsize[1]
    isoNoOutWetlandID = set()
    isoMultiOutWetlandID = set()
    iso1OutWetlandID = set()
    for id in wetlandCount:
        area = wetlandCount[id] * pixelArea
        if area < lowerThresholdArea or id in conflictWetlands:
            isoNoOutWetlandID.add(id)
        if id in riparianWetlandIDs:
            if id in isoNoOutWetlandID:
                riparianWetlandIDs.remove(id)
            continue
        if area > upperThresholdArea:
            isoMultiOutWetlandID.add(id)
        elif area >= lowerThresholdArea:
            iso1OutWetlandID.add(id)

    f = os.path.splitext(wetlandRasFile)[0]

    if isoMultiOutWetlandID:
        wetIsoMOut = f"{f}_IsoMOut.dep"
        wetlandIsoMOutRaster = np.load(wetIsoMOut)
        for row in range(rows):
            for col in range(cols):
                if wetlandID[row, col] > 0 and wetlandID[row, col] in isoMultiOutWetlandID:
                    wetlandIsoMOutRaster[row, col] = int(wetlandID[row, col])
                else:
                    wetlandIsoMOutRaster[row, col] = nodataWet
        np.save(wetIsoMOut, wetlandIsoMOutRaster)
    else:
        print("No wetland bigger than threshold!")

    if streamFile and riparianWetlandIDs:
        wetRipa = f"{f}_RipaOut.dep"
        wetlandRipaRaster = np.load(wetRipa)
        for row in range(rows):
            for col in range(cols):
                if wetlandID[row, col] > 0 and wetlandID[row, col] in riparianWetlandIDs:
                    wetlandRipaRaster[row, col] = int(wetlandID[row, col])
                else:
                    wetlandRipaRaster[row, col] = nodataWet
        np.save(wetRipa, wetlandRipaRaster)

    wetIso1Out = f"{f}_Iso1Out.dep"
    wetlandIso1OutRaster = np.load(wetIso1Out)
    wetIsolate = f"{f}_Isolate.dep"
    wetlandIsolateRaster = np.load(wetIsolate)
    wetMdfy = f"{f}_Mdfy.dep"
    wetlandMdfy = np.load(wetMdfy)

    endNodes = None
    hasEndNode = bool(endNodeFile)
    if hasEndNode:
        endNodes = np.load(endNodeFile)
        print("End node file provided!")
    else:
        print("No end node file provided!")

    output = np.full((rows, cols), nodata)
    flowdir = np.zeros((rows, cols), dtype=np.int8)
    queue = PriorityQueue()
    inQueue = np.zeros((rows, cols), dtype=bool)

    oldProgress = -1
    for row in range(rows):
        for col in range(cols):
            z = dem[row, col]
            output[row, col] = z
            flowdir[row, col] = 0
            if z != nodata:
                isWetland = wetlandID[row, col] > 0
                isPit = True
                isEdgeCell = False
                for n in range(8):
                    zN = dem[row + int_dY[n], col + int_dX[n]]
                    if isPit and zN != nodata and zN < z:
                        isPit = False
                    elif zN == nodata:
                        isEdgeCell = True
                if (isPit and isEdgeCell) or (isWetland and isEdgeCell):
                    queue.put(GridCell(row, col, z, 0, isWetland))
                    inQueue[row, col] = True
            else:
                numSolvedCells += 1
        progress = int(100 * row / rowsLessOne)
        if progress > oldProgress:
            oldProgress = progress

    oldProgress = int(100 * numSolvedCells / numCellsTotal)
    flatIndex = 0
    k = 0
    linkIDValue, linkIDValueN = 0, 0
    while not queue.empty():
        gc = queue.get()
        row = gc.row
        col = gc.col
        flatIndex = gc.flatIndex
        linkIDValue = wetlandID[row, col]
        isWetland = linkIDValue > 0
        if linkIDValue > 0:
            flag = True
            r = row
            j = col
            while flag:
                indexOfNextCell = -1
                minPosDiff = float('inf')
                posDiff = 0
                position = wetlandPosition[r, j]
                for n in range(8):
                    rowN = r + int_dY[n]
                    colN = j + int_dX[n]
                    linkIDValueN = wetlandID[rowN, colN]
                    if linkIDValueN == linkIDValue and not inQueue[rowN, colN] and wetlandPosition[rowN, colN] > 0:
                        positionN = wetlandPosition[rowN, colN]
                        posDiff = (positionN - position) ** 2
                        if posDiff < minPosDiff:
                            minPosDiff = posDiff
                            indexOfNextCell = n
                    elif linkIDValueN == -32768 or wetlandEndNodes[rowN, colN] or wetlandPosition[rowN, colN] < 0:
                        zN = output[rowN, colN]
                        if zN != nodata and not inQueue[rowN, colN]:
                            numSolvedCells += 1
                            flowdir[rowN, colN] = backLink[n]
                            k = 0
                            if zN == output[row, col]:
                                k = flatIndex + 1
                            queue.put(GridCell(rowN, colN, zN, k, wetlandEndNodes[rowN, colN]))
                            inQueue[rowN, colN] = True
                if indexOfNextCell > -1:
                    rowN = r + int_dY[indexOfNextCell]
                    colN = j + int_dX[indexOfNextCell]
                    numSolvedCells += 1
                    flowdir[rowN, colN] = backLink[indexOfNextCell]
                    inQueue[rowN, colN] = True
                    r = rowN
                    j = colN
                else:
                    flag = False
        else:
            for n in range(8):
                rowN = row + int_dY[n]
                colN = col + int_dX[n]
                zN = output[rowN, colN]
                if zN != nodata and not inQueue[rowN, colN]:
                    linkIDValueN = wetlandID[rowN, colN]
                    if linkIDValueN == -32768 or wetlandEndNodes[rowN, colN]:
                        numSolvedCells += 1
                        flowdir[rowN, colN] = backLink[n]
                        k = 0
                        if zN == output[row, col]:
                            k = flatIndex + 1
                        queue.put(GridCell(rowN, colN, zN, k, wetlandEndNodes[rowN, colN]))
                        inQueue[rowN, colN] = True
        progress = int(100 * numSolvedCells / numCellsTotal)
        if progress > oldProgress:
            oldProgress = progress

    outputRaster = np.load(outputFile)
    for row in range(rows):
        for col in range(cols):
            z = output[row, col]
            if z != nodata:
                outputRaster[row, col] = outPointer[flowdir[row, col]]
        progress = int(100 * row / rowsLessOne)
        if progress > oldProgress:
            oldProgress = progress

    dem.close()
    wetlandRas.close()

    outputRaster.setPreferredPalette(paletteName)
    outputRaster.addMetadataEntry("Created by the " + self.getDescriptiveName() + " tool.")
    outputRaster.addMetadataEntry("Created on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    outputRaster.close()

    self.returnData(outputFile)


