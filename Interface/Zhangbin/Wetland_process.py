# -*- coding: utf-8 -*-
"""
@Time ： 2024/5/28 21:52
@Auth ： Bin Zhang
@File ：Wetland_process.py
@IDE ：PyCharm
"""
import Raster  # Raster is my functions used frequently, which are about raster data
import numpy as np
from osgeo import gdal

dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}

def get_rever_D8(dir, row, col):
    """
    查询输入栅格的上游栅格
    :param dir: array of dir
    :param row: row of the cell
    :param col:
    :return: [(i,j),(),]
    """
    up_cell = []
    row_num, col_num = dir.shape

    for i in range(8):
        now_loc = (row + dmove[i][0], col + dmove[i][1])
        # print(now_loc)
        if 0<=now_loc[0]<row_num and 0<=now_loc[1]<col_num:
            if dir[now_loc[0], now_loc[1]] == 2 ** ((i + 4) % 8):
                up_cell.append(now_loc)

    return up_cell

def Raise_watershed(Watershed, DEM, proj, geo, watershed_nodata, DEM_nodata):
    """
    Raise the height of the watershed's extent
    :param Watershed: raster of watershed breaking the outlet
    :param DEM:
    :param proj:
    :param geo:
    :param watershed_nodata:
    :param DEM_nodata:
    :return:
    """
    row, col = Watershed.shape
    for i in range(row):
        for j in range(col):
            if Watershed[i, j] != watershed_nodata:
                DEM[i, j] += 200  # default 200, can be changed

    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\DEM_raise.tif', DEM, proj, geo, gdal.GDT_Float32,
                       DEM_nodata)

def IMWEBS_wetland(wetland, Dir, Acc, Area_thre, Acc_thre, proj, geo, wetland_nodata, size=30):
    """
    1）首先找到湿地边界，寻找汇流累积量最大的3个cell，作为出口；
    对于其他流出的cell，强制流向湿地内；
    2）追溯每块湿地的上游
    :param wetland: Raster of wetlands
    :param Dir: Flow direction
    :param Acc: Flow accumulation
    :param Area_thre: threshold of Area, which is used to judge if the wetland can be split
    :param Acc_thre: threshold of accumulation,which is used to judge if the cell of extent can be the outlet
    :param proj:
    :param geo:
    :param wetland_nodata:
    :param size: size of cell
    :return:
    """
    row, col = wetland.shape
    Vis = np.zeros((row, col))
    Result = np.zeros((row, col))
    Result[:, :] = -9999
    Vis1 = np.zeros((row, col))
    Vis2 = np.zeros((row, col))
    id = 1
    wetland_extent = np.zeros((row, col))
    wetland_extent[:, :] = -9999
    OUTLET = np.zeros((row, col))
    OUTLET[:, :] = -9999
    WETLAND = wetland
    out = np.zeros((row, col))
    out[:, :] = -9999
    for i in range(row):
        for j in range(col):
            if wetland[i, j] != wetland_nodata:
                # print(id)
                now_wetland_id = wetland[i, j]
                extent = []
                wetland_cells = []
                Wetland_Area = 0
                if Vis[i, j] == 0:
                    # 搜索邻域内湿地并标记边界栅格
                    pop_cells = [(i, j)]  # 迭代列表
                    Vis[i, j] = 1  # 标记已遍历
                    temp_A = []
                    while pop_cells:
                        pop_cell = pop_cells.pop()
                        wetland_cells.append(pop_cell)
                        temp_A.append(pop_cell)
                        Wetland_Area += size * size
                        # 搜索8邻域内cell
                        flag = False
                        for k in range(8):
                            next_cell = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])
                            if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                # if wetland[next_cell[0], next_cell[1]] != wetland[pop_cell[0], pop_cell[1]]:
                                #     flag = True

                                if Vis[next_cell[0], next_cell[1]] == 0 and wetland[next_cell[0], next_cell[1]] == \
                                        wetland[i, j]:
                                    pop_cells.append(next_cell)
                                    Vis[next_cell[0], next_cell[1]] = 1

                    # 判断是否为边界栅格
                    for cell in temp_A:
                        for k in range(8):
                            next_cell = (cell[0] + dmove[k][0], cell[1] + dmove[k][1])
                            if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                if wetland[next_cell[0], next_cell[1]] != wetland[i, j]:
                                    extent.append((cell[0], cell[1], Acc[cell[0], cell[1]]))
                                    break
                            else:
                                extent.append((cell[0], cell[1], Acc[cell[0], cell[1]]))
                                break
                for cell in extent:
                    wetland_extent[cell[0], cell[1]] = 1

                # 判断是否为边界栅格
                # 处理当前湿地
                # 1、寻找出口
                outlets = []

                Method = 1
                extent.sort(key=lambda x: x[2], reverse=True)  # 对汇流累积量排序  ！！！！！！！流出的最大！！！！！！！！！！！！！！！！！！
                # print(extent)
                temp_num = 0
                for ii in range(len(extent)):  # 最多指定3个出口，小于阈值的不作为出口
                    if temp_num >= 3:
                        break
                    # 先判断是否流出，再判断Acc阈值
                    now_dir = Dir[extent[ii][0], extent[ii][1]]
                    if now_dir in dmove_dic:
                        ds_cell = (extent[ii][0] + dmove_dic[now_dir][0], extent[ii][1] + dmove_dic[now_dir][1])
                        if 0 <= ds_cell[0] < row and 0 <= ds_cell[1] < col:
                            if wetland[ds_cell[0], ds_cell[1]] != wetland[extent[ii][0], extent[ii][1]]:
                                out[extent[ii][0], extent[ii][1]] = 2
                                # 流向湿地外，判断Acc阈值
                                if extent[ii][2] >= Acc_thre:
                                    outlets.append(extent[ii])
                                    OUTLET[extent[ii][0], extent[ii][1]] = 1
                                    temp_num += 1
                if Wetland_Area <= Area_thre:
                    for cell in outlets[1:]:
                        outlets.remove(cell)
                        OUTLET[cell[0], cell[1]] = -9999

                # 如果面积小于阈值则outlets==[]，此时说明湿地没有流向外面的cell，则以SEIMS方式处理
                # print(outlets)
                if len(outlets) == 0:
                    # print('**')
                    # outlets=extent.copy()
                    # outlets=wetland_cells.copy()
                    Method = 2

                if Method == 2:
                    # SEIMS:按照湿地边界追溯上游
                    cells = wetland_cells.copy()
                    # print(cells)
                    # print(extent)
                    while cells:
                        cell = cells.pop()
                        Result[cell[0], cell[1]] = id
                        Us_cells = get_rever_D8(Dir, cell[0], cell[1])
                        for temp_cell in Us_cells:
                            if Vis1[temp_cell[0], temp_cell[1]] == 0:
                                if wetland[temp_cell[0], temp_cell[1]] == wetland_nodata:
                                    cells.append(temp_cell)
                                    Vis1[temp_cell[0], temp_cell[1]] = 1
                                    # Result[temp_cell[0], temp_cell[1]] = id
                    id += 1
                if Method == 1:

                    # IMWEBS:先分割湿地，再回溯上游
                    # 2、强制边界cell流向湿地
                    pop_cells = outlets.copy()  # 迭代列表
                    # print(pop_cells)
                    for cell_1 in outlets:
                        wetland_extent[cell_1[0], cell_1[1]] = 2
                    while pop_cells:
                        pop_cell = pop_cells.pop()
                        # print(pop_cell)
                        for k in range(8):
                            next_cell_1 = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])  # 临时变量
                            if 0 <= next_cell_1[0] < row and 0 <= next_cell_1[1] < col:  # 保证cell有效
                                next_cell = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1],
                                             Acc[next_cell_1[0], next_cell_1[1]])
                                if wetland_extent[next_cell[0], next_cell[1]] == 1:
                                    # 如果是下游是流出湿地，则纠正流向
                                    next_cell_dir = Dir[next_cell[0], next_cell[1]]
                                    if next_cell_dir in dmove_dic:
                                        temp_next_cell = (next_cell[0] + dmove_dic[next_cell_dir][0],
                                                          next_cell[1] + dmove_dic[next_cell_dir][1])
                                        if 0 <= temp_next_cell[0] < row and 0 <= temp_next_cell[1] < col:
                                            if wetland[temp_next_cell[0], temp_next_cell[1]] != wetland[
                                                next_cell[0], next_cell[1]]:
                                                Dir[next_cell[0], next_cell[1]] = 2 ** ((k + 4) % 8)
                                        wetland_extent[next_cell[0], next_cell[1]] = 2
                                        pop_cells.insert(0, next_cell)

                    # 3、追溯wetland上游
                    for cell in outlets:
                        Vis9 = np.zeros((row, col))
                        cells = [cell]
                        Vis9[cell[0], cell[1]] = 1
                        while cells:
                            pop_cell = cells.pop()
                            Result[pop_cell[0], pop_cell[1]] = id
                            Us_cells = get_rever_D8(Dir, pop_cell[0], pop_cell[1])
                            for temp_cell in Us_cells:
                                if Vis9[temp_cell[0], temp_cell[1]] == 0:
                                    if wetland[temp_cell[0], temp_cell[1]] == wetland_nodata or wetland[
                                        temp_cell[0], temp_cell[1]] == now_wetland_id:
                                        cells.append(temp_cell)
                                        Vis9[temp_cell[0], temp_cell[1]] = 1
                        id += 1

    # 重构湿地
    Vis1[:, :] = 0
    second = {}
    for i in range(row):
        for j in range(col):
            if wetland[i, j] != wetland_nodata:
                WETLAND[i, j] = Result[i, j]
            if wetland[i, j] != wetland_nodata and Result[i, j] == -9999:
                # 分割湿地后，有些湿地没有出口，需要再追溯上游
                second.setdefault(wetland[i, j], []).append((i, j))
    for wet_ in second:
        wetland_cells = second[wet_]

        while wetland_cells:
            pop_cell = wetland_cells.pop()
            Result[pop_cell[0], pop_cell[1]] = id
            Us_cells = get_rever_D8(Dir, pop_cell[0], pop_cell[1])
            for temp_cell in Us_cells:
                if Vis1[temp_cell[0], temp_cell[1]] == 0:
                    if wetland[temp_cell[0], temp_cell[1]] == wetland_nodata or wetland[
                        temp_cell[0], temp_cell[1]] == wet_:
                        wetland_cells.append(temp_cell)
                        Vis1[temp_cell[0], temp_cell[1]] = 1
        id += 1

    # 重构编码
    us = {}
    wet = {}
    for i in range(row):
        for j in range(col):
            if Result[i, j] != -9999:
                us.setdefault(Result[i, j], []).append((i, j))
            if WETLAND[i, j] != wetland_nodata:
                wet.setdefault(WETLAND[i, j], []).append((i, j))
    Result[:, :] = -9999
    id = 1
    for wet_ in us:
        wetland_cells = us[wet_]

        for cell in wetland_cells:
            Result[cell[0], cell[1]] = id
        id += 1

    for i in range(row):
        for j in range(col):
            if WETLAND[i, j] != wetland_nodata:
                WETLAND[i, j] = Result[i, j]

    # 输出结果
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\LS2.tif', Result, proj, geo, gdal.GDT_Float32,-9999)
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\wetex.tif', wetland_extent, proj, geo,gdal.GDT_Float32, -9999)
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\OUTLETS.tif', OUTLET, proj, geo, gdal.GDT_Float32,-9999)
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\WETLAND.tif', WETLAND, proj, geo,gdal.GDT_Float32, wetland_nodata)
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\Dir_modified.tif', Dir, proj, geo, gdal.GDT_Byte,0)
    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\D_OUT.tif', out, proj, geo, gdal.GDT_Float32,-9999)   # It is not important

def build_wetland_flow_path(OutLet, Dir, wetland, LS, nodata, proj, geo):
    """

    Build the flow path within the wetlands.

    :param OutLet: Outlets of wetlands
    :param Dir: Flow direction
    :param Wetland: Raster of the wetlands
    :param LS: Output result, Upstream of the wetlands
    :param nodata: Nodata of the Wetland
    :return:
    """
    row, col = wetland.shape
    Done = np.zeros((row, col))
    Vis = np.zeros((row, col))
    flow_tree = {}
    ROAD = np.zeros((row, col))
    for i in range(row):
        for j in range(col):
            if OutLet[i, j] != -9999:
                # 找到出口，开始寻找下游
                pop_cells = [(i, j)]
                temp_road = [(i, j)]
                # Vis[i, j] = 1
                next_wetland_id = -1  # 没有下游湿地（流向边界外的或者洼地）为-1
                now_wetland_id = LS[i, j]
                while pop_cells:
                    pop_cell = pop_cells.pop()
                    # print(pop_cell)
                    now_dir = Dir[pop_cell[0], pop_cell[1]]
                    if now_dir in dmove_dic:
                        next_cell = (pop_cell[0] + dmove_dic[now_dir][0], pop_cell[1] + dmove_dic[now_dir][1])
                        if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:
                            if Vis[next_cell[0], next_cell[1]] == 0:
                                if wetland[next_cell[0], next_cell[1]] != nodata and wetland[next_cell[0], next_cell[1]] != now_wetland_id:
                                    next_wetland_id = LS[next_cell[0], next_cell[1]]
                                    if OutLet[next_cell[0], next_cell[1]] != -9999:
                                        break
                                pop_cells.append(next_cell)
                                if next_cell in temp_road:
                                    break
                                temp_road.append(next_cell)
                                # Vis[next_cell[0], next_cell[1]] = 1
                # 回溯路径
                # print(temp_road)
                for cell in temp_road:
                    Done[cell[0], cell[1]] = next_wetland_id
                    ROAD[cell[0], cell[1]] = 1
                flow_tree.setdefault(wetland[i, j], set()).add(next_wetland_id)

    f = open(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\flow_tree.txt', 'w')  # 输出的湿地的上下游关系
    for i in flow_tree:
        f.write(str(i) + ':' + str(flow_tree[i]) + '\n')
        print(i, flow_tree[i])

    Raster.save_raster(r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\ROAD1.tif', ROAD, proj, geo, gdal.GDT_Byte,0)  # 输出的栅格流路文件，

if __name__=='__main__':


    # ********************** First,run Raise_watershed *************************
    # The path of input files
    Watershed_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Watershed_raster.tif'
    Burn_DEM_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Burn_DEM.tif'

    # Open data,get array,projection,geotranform,nodata
    Watershed_extent=Raster.get_raster(Watershed_file)
    Burn_DEM=Raster.get_raster(Burn_DEM_file)
    proj,geo,watershed_nodata=Raster.get_proj_geo_nodata(Watershed_file)
    _,_,DEM_nodata=Raster.get_proj_geo_nodata(Burn_DEM_file)

    # run function,remember to change the path of the output results,which are located at the end of the function.
    Raise_watershed(Watershed_extent,Burn_DEM,proj,geo,watershed_nodata,DEM_nodata)

    # ************************* Second,run IMWEBS_wetland **************************
    # The path of input files
    wetland_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\wetland.tif'
    Dir_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Dir.tif'
    Acc_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\ACC.tif'

    # Open data,get array,projection,geotranform,nodata
    wetland=Raster.get_raster(wetland_file)
    Dir=Raster.get_raster(Dir_file)
    Acc=Raster.get_raster(Acc_file)
    proj,geo,wetland_nodata=Raster.get_proj_geo_nodata(wetland_file)
    Area_thre=45000  # 0.045 km2
    Acc_thre=0
    size=15  # size of cell
    # run function,remember to change the path of the output results,which are located at the end of the function.
    IMWEBS_wetland(wetland,Dir,Acc,Area_thre,Acc_thre,proj,geo,wetland_nodata,size)

    # ************************* Third,run build_wetland_flow_path *************************
    # Note:The input files are all the second function's output results.
    Outlet_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\OUTLETS.tif'
    Dir_modified_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\Dir_modified.tif'   # It is the modified Dir,which is dfferent from the second Dir.
    wetland_modified_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\WETLAND.tif'   # It is the modified wetland,which is dfferent from the second wetland.
    LS_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\LS2.tif'

    # Open data,get array,projection,geotranform,nodata
    Outlet=Raster.get_raster(Outlet_file)
    Dir_modified=Raster.get_raster(Dir_modified_file)
    wetland_modified=Raster.get_raster(wetland_modified_file)
    LS=Raster.get_raster(LS_file)
    proj,geo,wetland_nodata=Raster.get_proj_geo_nodata(wetland_modified_file)

    # run function,remember to change the path of the output results,which are located at the end of the function.
    build_wetland_flow_path(Outlet,Dir_modified,wetland_modified,LS,wetland_nodata,proj,geo)

    # Note: Above functions output the raster result(.tif). If users want to get shapefile,they need to make by tools of Arcgis/wbt.

    pass