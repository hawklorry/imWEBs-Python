
import numpy as np
import pandas as pd
from .reach_parameter import ReachParameter
from ...raster_extension import RasterExtension
from whitebox_workflows import Raster
import math

import logging
logger = logging.getLogger(__name__)

class Reach:
    """
    This genenates all the reach parameters. Some of the parameters use default values. 
    The ReachParameter class provides the table structure and default values. 
    This replaces the Reach.Java with perforamce improvements with whitebox workflow built-in functions like zonal_statistics.
    The loops should avoided whenever possible. 

    Replace buildReachParTable
    """
    def __init__(self, 
                 dem_raster:Raster, 
                 subbasin_raster:Raster, 
                 stream_network_raster:Raster, 
                 stream_order_raster:Raster, 
                 flow_length_raster:Raster, 
                 flow_direction_raster:Raster,
                 flow_accumulation_raster:Raster,
                 reach_width_raster:Raster, 
                 reach_depth_raster:Raster,                 
                 velocity_raster:Raster):
        self.LnOf2 = 0.693147180559945
        self.minimumSlope = 0.01

        self.subbasin_raster = subbasin_raster  
        self.stream_network_raster = stream_network_raster
        self.reach_length_raster = flow_length_raster
        self.flow_dir_raster = flow_direction_raster
        self.stream_order_raster = stream_order_raster
        self.reach_width_raster = reach_width_raster
        self.reach_depth_raster = reach_depth_raster
        self.dem_raster = dem_raster
        self.velocity_raster = velocity_raster
        self.flow_acc_raster = flow_accumulation_raster
        
        self.subMax = int(RasterExtension.get_max_value(self.subbasin_raster))
        self.rowNum = int(self.stream_network_raster.configs.rows)
        self.colNum = int(self.stream_network_raster.configs.columns)

        self.cellsize = dem_raster.configs.resolution_x
        self.cellsize_ha = dem_raster.configs.resolution_x * dem_raster.configs.resolution_y / 10000    
        self.min_length = (dem_raster.configs.resolution_x + dem_raster.configs.resolution_y) / 4
        self.nodata = dem_raster.configs.nodata

        self.dX = [1, 1, 1, 0, -1, -1, -1, 0]
        self.dY = [-1, 0, 1, 1, 1, 0, -1, -1]

    def __calculate_reach_length(self):
        rchmax = np.zeros(self.subMax)
        rchmin = np.zeros(self.subMax)
        rch_in_row = np.zeros(self.subMax, dtype=int)  # the row of in point of main stream
        rch_in_col = np.zeros(self.subMax, dtype=int)  # the col of in point of main stream
        rch_in_row2 = np.zeros(self.subMax, dtype=int)  # the row of in point of main stream which doesn't has upstream
        rch_in_col2 = np.zeros(self.subMax, dtype=int)  # the row of in point of main stream which doesn't has upstream
        currentSub = 0


        for i in range(0, self.subMax):
            rchmax[i] = 0
            rchmin[i] = self.reach_length_raster.configs.maximum
            rch_in_row[i] = -1
            rch_in_col[i] = -1
            rch_in_row2[i] = -1
            rch_in_col2[i] = -1

        for row in range(self.rowNum):
            for col in range(self.colNum):
                currentValue = self.reach_length_raster[row, col]
                currentSub = int(self.subbasin_raster[row, col])
                if currentValue > 0 and currentSub > 0 and self.stream_network_raster[row, col] > 0:
                    if currentValue > rchmax[currentSub - 1]:
                        rchmax[currentSub - 1] = currentValue

                    if currentValue < rchmin[currentSub - 1]:
                        rchmin[currentSub - 1] = currentValue
                        rch_in_row2[currentSub - 1] = row
                        rch_in_col2[currentSub - 1] = col

                    if rch_in_row[currentSub - 1] == -1:
                        flowDir = -1
                        previousSubID = currentSub
                        nextRow = row
                        nextCol = col
                        flag = True
                        while flag:
                            flowDir = self.flow_dir_raster[nextRow, nextCol]
                            if flowDir > 0:
                                c = int(np.log(flowDir) / self.LnOf2)
                                if c > 7:
                                    print("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")
                                    flag = False
                                    break
                                nextCol += self.dX[c]
                                nextRow += self.dY[c]
                                if self.stream_network_raster[nextRow, nextCol] < 0:  # not stream
                                    flag = False
                                    break
                                subID = int(self.subbasin_raster[nextRow, nextCol])
                                if subID < 0:
                                    flag = False
                                    break
                                if previousSubID != subID:  # go into next subbasin
                                    if rch_in_row[subID - 1] != -1:  # already found
                                        flag = False
                                        break
                                    rch_in_row[subID - 1] = nextRow
                                    rch_in_col[subID - 1] = nextCol
                                    previousSubID = subID

                                if self.reach_length_raster[nextRow, nextCol] >= self.reach_length_raster.configs.maximum:  # outlet
                                    flag = False
                                    break
                            else:
                                flag = False
                                break

        for i in range(self.subMax):
            if rch_in_row[i] != -1:
                rchmin[i] = self.reach_length_raster[rch_in_row[i], rch_in_col[i]]
            else:
                rchmin[i] = 0
                rch_in_row[i] = rch_in_row2[i]
                rch_in_col[i] = rch_in_col2[i]

        return rch_in_row, rch_in_col, np.maximum(rchmax - rchmin, self.min_length) 

    def __calculate_reach_mean(self, value_raster, name:str, min_value = None):
        #filter out the raster that are not on a stream       
        raster = self.stream_network_raster.con(f"value == {self.stream_network_raster.configs.nodata}", self.nodata, value_raster)

        #get the mean width in each subbasin
        reach_width_df = RasterExtension.get_zonal_statistics(raster, self.subbasin_raster, "mean", name)

        #use min value if available
        if min_value is not None:
            reach_width_df[name] = np.where(reach_width_df[name] < min_value, min_value, reach_width_df[name])

        #return the np array
        return reach_width_df[name].to_numpy()

    def __calculate_reach_width(self):
        """
        Mean width of cells on each reach        
        """
        return self.__calculate_reach_mean(self.reach_width_raster, "width", 0.1)

    def __calculate_reach_depth(self)->pd.DataFrame:
        """
        Mean depth of cells on each reach        
        """
        return self.__calculate_reach_mean(self.reach_depth_raster, "depth", 0.1)
    
    def __calculate_reach_velocity(self):
        """
        Mean velocity of cells on each reach        
        """
        return self.__calculate_reach_mean(self.velocity_raster, "veloctiy")

    def __calculate_reach_slope(self, rch_in_row, rch_in_col):
        rchavg = np.zeros(self.subMax)

        dx1 = self.cellsize
        dx2 = dx1 * np.sqrt(2.0)

        for i in range(self.subMax):
            totalSlope = 0.0
            totalCell = 1  # H.Shao >> 160404-01 <<
            flowDir = -1
            previousRow = rch_in_row[i]
            previousCol = rch_in_col[i]
            nextRow = rch_in_row[i]
            nextCol = rch_in_col[i]

            flag = True
            while flag:
                flowDir = self.flow_dir_raster[nextRow, nextCol]
                if flowDir > 0:
                    c = int(np.log(flowDir) / self.LnOf2)
                    if c > 7:
                        print("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")
                        flag = False
                        break
                    nextCol += self.dX[c]
                    nextRow += self.dY[c]

                    dy1 = self.dem_raster[previousRow, previousCol] - self.dem_raster[nextRow, nextCol]
                    dx3 = self.dX[c] * self.dY[c] == 0 and dx1 or dx2

                    totalSlope += dy1 / dx3
                    totalCell += 1

                    previousRow = nextRow
                    previousCol = nextCol

                    subID = int(self.subbasin_raster[nextRow, nextCol])
                    if i != subID - 1:  # go into next subbasin or border, then stop
                        flag = False
                        break
                else:
                    flag = False
                    break

            rchavg[i] = 0
            rchavg[i] = np.maximum(totalSlope / totalCell * 100.0, self.minimumSlope)

        return rchavg
    
    def __calculate_reach_order(self):
        """
        Just get max order for each subbasin
        """

        reach_order_df = RasterExtension.get_zonal_statistics(self.stream_order_raster, self.subbasin_raster, ["max"], "order")
        default_reach_order_df = pd.DataFrame(index=range(1, self.subMax + 1))
        default_reach_order_df["order"] = 1

        reach_order_df = reach_order_df.combine_first(default_reach_order_df)

        #return the np array
        return reach_order_df["order"].to_numpy()

    def __calculate_reach_manning(self,rch_in_row, rch_in_col):
        """
        Manning is linearly interpolated from a min and max manning based on stream order raster. 

        It seems there is no need to do the way it is. Just simply loop through each reach and do the 
        linear interpolation as the stream order is calculated for each reach.
        """
        rchavg = np.zeros(self.subMax)

        minReachManning = -0.1
        maxReachManning = -0.04
        unitManning = (maxReachManning - minReachManning) / (self.stream_order_raster.configs.maximum - self.stream_order_raster.configs.minimum)

        for i in range(self.subMax):
            totalManning = 0.0
            totalManningNum = 0
            nextStreamOrder = -1
            previousStreamOrder = -1
            nextRow = rch_in_row[i]
            nextCol = rch_in_col[i]

            flag = True
            while flag:
                # calculate manning
                nextStreamOrder = self.stream_order_raster[nextRow, nextCol]
                if previousStreamOrder != nextStreamOrder:
                    totalManning += minReachManning + unitManning * (nextStreamOrder - self.stream_order_raster.configs.minimum)
                    totalManningNum += 1
                    previousStreamOrder = nextStreamOrder

                flowDir = self.flow_dir_raster[nextRow, nextCol]
                if flowDir > 0:
                    c = int(np.log(flowDir) / self.LnOf2)
                    if c > 7:
                        print("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")
                        flag = False
                        break
                    nextCol += self.dX[c]
                    nextRow += self.dY[c]
                else:
                    flag = False
                    break

                subID = int(self.subbasin_raster[nextRow, nextCol])
                if i != subID - 1:
                    flag = False
                    break

            rchavg[i] = max(min(-1 * totalManning / totalManningNum, 0.1), 0.04)

        return rchavg

    def __calculate_receive_reach_id(self):
        rchavg = np.zeros(self.subMax, dtype=int)

        for i in range(self.subMax):
            rchavg[i] = -1

        for row in range(self.rowNum):
            for col in range(self.colNum):
                currentSub = int(self.subbasin_raster[row, col])
                if currentSub > 0:
                    for i in range(self.subMax):
                        if rchavg[i] == -1 and currentSub == i + 1:
                            currentRch = currentSub
                            nextCol = col
                            nextRow = row

                            flag = True
                            flowDir = -1
                            # H.Shao >> 160510-01
                            checkDownStream = 5  # Check 5 downstreams to see if there is loop flow path
                            checkList = []
                            tempRch = -1
                            # H.Shao << 160510-01
                            while flag:
                                flowDir = self.flow_dir_raster[nextRow, nextCol]
                                if flowDir > 0:
                                    c = int(np.log(flowDir) / self.LnOf2)
                                    if c > 7:
                                        print("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")
                                        flag = False
                                        break
                                    nextCol += self.dX[c]
                                    nextRow += self.dY[c]

                                    nextRch = int(self.subbasin_raster[nextRow, nextCol])

                                    if nextRch != currentRch or checkList:
                                        if not checkList:
                                            tempRch = nextRch

                                        if nextRch not in checkList:
                                            checkList.append(nextRch)

                                        if nextRch == currentRch:
                                            checkList = []
                                            tempRch = -1
                                            continue
                                        if (len(checkList) == checkDownStream and currentRch not in checkList) or nextRch < 0:
                                            if tempRch > 0:
                                                rchavg[currentRch - 1] = tempRch
                                                flag = False
                                            else:
                                                rchavg[currentRch - 1] = 0
                                                flag = False

                                else:
                                    if tempRch > 0:
                                        rchavg[currentRch - 1] = tempRch
                                        flag = False
                                    else:
                                        rchavg[currentRch - 1] = 0
                                        flag = False
                                    flag = False
                                    break

        return np.maximum(rchavg, 0)

    def __calculate_contribution_area(self):
        """
        Basically get the max flow_acc in each subbasin and multipy the cell area
        """
        #get the mean depth in each subbasin
        reach_contribution_area_df = RasterExtension.get_zonal_statistics(self.flow_acc_raster, self.subbasin_raster, "max", "contri")

        #get the area
        reach_contribution_area_df = reach_contribution_area_df * self.cellsize_ha

        #return numpy array
        #logger.info(reach_contribution_area_df)
        return reach_contribution_area_df["contri"].to_numpy()

    def __calculate_reach_elevation(self):
        #filter out the raster that are not on a stream       
        raster = self.stream_network_raster.con(f"value == {self.stream_network_raster.configs.nodata}", self.nodata, self.dem_raster)

        #get the mean width in each subbasin
        reach_elevation_df = RasterExtension.get_zonal_statistics(raster, self.subbasin_raster, ["max","min","mean"])

        #return the np array
        return reach_elevation_df["max"].to_numpy(), reach_elevation_df["min"].to_numpy(),reach_elevation_df["mean"].to_numpy()

    @property
    def reach_parameter_df(self)->pd.DataFrame:
        reach_parameters = []
        for row in range(self.subMax):
            reach_parameters.append(ReachParameter())
        reach_parameter_table = pd.DataFrame([p.to_dict() for p in reach_parameters])
        reach_parameter_columns = reach_parameter_table.columns

        # Column 0 --- Reach ID "#reach_id"
        reach_parameter_table[reach_parameter_columns[0]] = range(1, self.subMax + 1)
        # Column 1 --- Subbasin ID "subbasin_id"
        reach_parameter_table[reach_parameter_columns[1]] = range(1, self.subMax + 1)
        # Column 2 --- Outlet ID "outlet_id"
        reach_parameter_table[reach_parameter_columns[2]] = range(1, self.subMax + 1)

        # Column 3 --- Reach length "length"
        rch_in_row, rch_in_col, reach_length = self.__calculate_reach_length()
        reach_parameter_table[reach_parameter_columns[3]] = reach_length

        # Column 4 --- Reach width "width"
        reach_parameter_table[reach_parameter_columns[4]] = self.__calculate_reach_width()

        # Column 8 --- Reach depth "depth"
        reach_parameter_table[reach_parameter_columns[8]] = self.__calculate_reach_depth()

        # Column 9 --- Reach slope "slope" -- unit of %
        reach_parameter_table[reach_parameter_columns[9]] = self.__calculate_reach_slope(rch_in_row, rch_in_col)

        # Column 10 --- Reach order "order"       
        reach_parameter_table[reach_parameter_columns[10]] = self.__calculate_reach_order()

        # Column 11 --- Manning's coefficient "manning"
        reach_parameter_table[reach_parameter_columns[11]] = self.__calculate_reach_manning(rch_in_row, rch_in_col)

        # Column 12 --- Velocity "velocity"
        reach_parameter_table[reach_parameter_columns[12]] = self.__calculate_reach_velocity()

        # Column 15, 16, 17 --- Max, Min, and Average elevation "max_elevation", "min_elevation", "ave_elevation"
        max_elev, min_elev, ave_elev = self.__calculate_reach_elevation()
        reach_parameter_table[reach_parameter_columns[15]] = max_elev
        reach_parameter_table[reach_parameter_columns[16]] = min_elev
        reach_parameter_table[reach_parameter_columns[17]] = ave_elev

        # Column 18 --- Receiving stream reach ID "receive_reach_id"
        reach_parameter_table[reach_parameter_columns[18]] = self.__calculate_receive_reach_id()

        # Column 19 --- Subbasin contribution area "contribution_area"
        reach_parameter_table[reach_parameter_columns[19]] = self.__calculate_contribution_area() 

        return reach_parameter_table


