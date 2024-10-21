import numpy as np
from ..names import Names
from whitebox_workflows import Raster, WbEnvironment, RasterDataType, Vector, AttributeField, FieldDataType, FieldData
from ..folder_base import FolderBase
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
from .structure_attribute import StructureAttribute
import heapq
from dataclasses import dataclass, field
import math
from collections import defaultdict
import logging
import os

logger = logging.getLogger(__name__)

class Structure(FolderBase):    
    """
    Structure processing to get the outlet and modified structure and flow direction. 
    This apply to wetland, Feedlot, Dugout, Catchbasin and Manure Storage

    A structure will have a boundary polygon shapefile and an optional outlet point shapefile. 
    """

    #catchbasin and manure storage is not included here as they don't impact the flow direction
    structure_types_affection_flow_direction = ["wetland","feedlot","wascob","dugout"]

    def __init__(self, structure_type:str, 
                 output_folder:str, 
                 dem_raster:Raster, 
                 structure_polygon_vector:Vector, 
                 structure_polygon_vector_id_field_name: str = Names.field_name_id,                 
                 structure_outlet_point_vector:Vector = None, 
                 structure_outlet_point_vector_id_field_name:str = Names.field_name_id,
                 structure_area_threshold_ha = 0, 
                 structure_allow_multiple_outlets = False,
                 structure_using_PFO = True):
        super().__init__(output_folder)

        self.structure_type = structure_type
        self.__structure_polygon_vector = structure_polygon_vector
        self.__structure_polygon_vector_id_field_name = structure_polygon_vector_id_field_name

        self.__structure_outlet_point_vector = structure_outlet_point_vector
        self.__structure_outlet_point_vector_id_field_name = structure_outlet_point_vector_id_field_name
        
        self.__dem_raster = dem_raster

        if self.__structure_polygon_vector is None:
            raise ValueError(f"{self.structure_type}: The structure polygon shapefile is empty.")
        exist, self.__structure_polygon_vector_id_field_name = VectorExtension.check_field_in_vector(self.__structure_polygon_vector, self.__structure_polygon_vector_id_field_name)
        if not exist:
            raise ValueError(f"{self.structure_type}: The given id field {self.__structure_polygon_vector_id_field_name} doesn't exist in boundary shapefile.")

        if self.__structure_outlet_point_vector is not None:
            if self.__structure_outlet_point_vector_id_field_name is None:
                raise ValueError(f"{self.structure_type}: The outlet shapefile id field name is empty.")
            exist, self.__structure_outlet_point_vector_id_field_name = VectorExtension.check_field_in_vector(self.__structure_outlet_point_vector, self.__structure_outlet_point_vector_id_field_name)
            if not exist:
                raise ValueError(f"{self.structure_type}: The given id field {self.__structure_outlet_point_vector_id_field_name} doesn't exist in outlet shapefile.")

        #area threshold lower that which the structures will be removed.
        self.__structure_area_threshold_ha = structure_area_threshold_ha

        #parameters for Shawn's method
        self.__structure_allow_multiple_outlets = structure_allow_multiple_outlets
        self.__structure_using_PFO = structure_using_PFO
        
        #parameters for Zhangbin's method
        #number of sub-structures that one structure will be split.
        #default 3 for wetland
        #defautl 1 for all other structures
        self.__structure_split_max_num = 1

        #the threshold of flow acc that will be consiered as outlet
        self.__structure_acc_theshold = 0

        #output file name
        self.__structure_boundary_original_raster_name = f"{self.structure_type}BoundaryOriginal{Names.raster_extension}"
        self.__structure_boundary_original_vector_name = f"{self.structure_type}BoundaryOriginal{Names.shapefile_extension}"

        self.__structure_boundary_processed_raster_name = f"{self.structure_type}BoundaryProcessed{Names.raster_extension}"
        self.__structure_boundary_processed_vector_name = f"{self.structure_type}BoundaryProcessed{Names.shapefile_extension}"

        self.__structure_outlet_original_raster_name = f"{self.structure_type}OutletOriginal{Names.raster_extension}"
        self.__structure_outlet_processed_raster_name = f"{self.structure_type}OutletProcessed{Names.raster_extension}"        
        self.__structure_outlet_processed_vector_name = f"{self.structure_type}OutletProcessed{Names.shapefile_extension}"


        #individual structure list
        self.__attributes = None
#region properties

    @property
    def boundary_original_vector(self):
        if self.__structure_area_threshold_ha <=0:
            return self.__structure_polygon_vector
        
        vector = self.get_vector(self.__structure_boundary_original_vector_name)
        if vector is None:
            vector = self.wbe.filter_vector_features_by_area(
                    self.__structure_polygon_vector, self.__structure_area_threshold_ha * 10000)
            
            self.save_vector(vector, self.__structure_boundary_original_vector_name)
        return vector


    @property
    def boundary_original_raster(self):
        """Original boundary raster"""
        raster = self.get_raster(self.__structure_boundary_original_raster_name)
        
        if raster is None:  
            logger.info(f"Converting {self.structure_type} boundary from shapefile ({self.boundary_original_vector.file_name}) to raster ...")
            raster = VectorExtension.vector_polygons_to_raster_with_boarder(
                                                        polygon_vector=self.boundary_original_vector, 
                                                        base_raster = self.__dem_raster, 
                                                        field_name = self.__structure_polygon_vector_id_field_name)
            self.save_raster(raster, self.__structure_boundary_original_raster_name)

        return raster

    @property
    def boundary_processed_vector(self)->Vector:
        """
        Processed boundary vector. The only change is adding a subbasin column and removing the structure that are not in any of subbasins.
        The original fields are still there
        """
        return self.get_vector(self.__structure_boundary_processed_vector_name)            

    @property
    def boundary_processed_raster(self)->Raster:
        """Process boundary raster where the structures that are not in any of subbasins are removed."""
        return self.get_raster(self.__structure_boundary_processed_raster_name)
    
    @property
    def boundary_raster(self)->Raster:
        """Final boundary raster"""
        if self.boundary_processed_raster is None:
            return self.boundary_original_raster
        
        return self.boundary_processed_raster    
            
    @property
    def outlet_raster(self)->Raster:
        """Final outlet raster"""
        return self.outlet_processed_raster
    
    @property
    def outlet_vector(self)->Vector:
        """Final outlet vector"""
        vector = self.get_vector(self.__structure_outlet_processed_vector_name)

        if vector is None:
            logger.info(f"Converting {self.structure_type} outlet from raster to vector ...")
            vector = VectorExtension.add_id_for_raster_value(RasterExtension.raster_to_vector(self.outlet_raster, "point"))
            self.save_vector(vector, self.__structure_outlet_processed_vector_name)

        return vector
    
    @property
    def outlet_original_raster(self)->Raster:
        """Original outlet raster"""      
        raster = self.get_raster(self.__structure_outlet_original_raster_name)        
        if raster is None and self.__structure_outlet_point_vector is not None:            
            logger.info(f"Converting {self.structure_type} outlet from shapefile ({self.__structure_outlet_point_vector.file_name}) to raster ...")
            raster = self.wbe.vector_points_to_raster(self.__structure_outlet_point_vector, 
                                                      base_raster = self.__dem_raster, 
                                                      field_name = self.__structure_outlet_point_vector_id_field_name)
            self.save_raster(raster, self.__structure_outlet_original_raster_name)

        return raster

    @property
    def outlet_processed_raster(self):
        """Processed outlet raster"""
        raster = self.get_raster(self.__structure_outlet_processed_raster_name)        

        if raster is None:
            if self.outlet_original_raster is not None:                
                raster = self.__offset_outlets()
            else:                
                raster = self.__find_outlets_shawn()
            self.save_raster(raster,self.__structure_outlet_processed_raster_name)

        return raster
    
    @property 
    def attributes(self)->dict:
        """structure attribute dictionary including id, area, subbasin and contribution area"""
        if self.__attributes is None:
            if self.boundary_processed_vector is None:
                raise ValueError(f"Processed vector for structure: {self.structure_type} doesn't exist. ")

            self.__attributes = {}
            for i in range(self.boundary_processed_vector.num_records):
                id = int(self.boundary_processed_vector.get_attribute_value(i, Names.field_name_id).get_value_as_f64())
                subbasin = int(self.boundary_processed_vector.get_attribute_value(i, Names.field_name_subbasin).get_value_as_f64())
                area = self.boundary_processed_vector.get_attribute_value(i, Names.field_name_area).get_value_as_f64() / 10000.0
                contibution_area = self.boundary_processed_vector.get_attribute_value(i, Names.field_name_contibution_area_ha).get_value_as_f64()
                
                self.__attributes[id] = StructureAttribute(id, area, subbasin, contibution_area)
        
        return self.__attributes 

#endregion

#region 
    
    def __creatd_processed_boundary_vector(self, id_subbasin_dict:dict, id_contribution_area_dict:dict)->Vector:
        """Add subbasin column to vector with the given id subbasin dictionary"""
       
        #creat all necessary fields
        #we will just use four columns: id, subbasin, contribution area and area. Area will be added by polygon_area function.
        fields = [
            AttributeField(Names.field_name_id, FieldDataType.Int, 6, 0),
            AttributeField(Names.field_name_subbasin, FieldDataType.Int, 6, 0),
            AttributeField(Names.field_name_contibution_area_ha, FieldDataType.Real, 12, 5)
        ]

        out_vector = self.wbe.new_vector(self.boundary_original_vector.header.shape_type, 
                                         fields,
                                         proj=self.boundary_original_vector.projection)

        # Now fill it with the input data
        for i in range(self.boundary_original_vector.num_records):
            id = int(self.boundary_original_vector.get_attribute_value(i, self.__structure_polygon_vector_id_field_name).get_value_as_f64())
            
            #remove those that are not included in subbasin
            if id not in id_subbasin_dict:
                continue
            
            #add geometry
            geom = self.boundary_original_vector[i]
            out_vector.add_record(geom) # Add the record to the output Vector

            #add fields
            field_data = [
                FieldData.new_int(id),
                FieldData.new_int(int(id_subbasin_dict[id])),
                FieldData.new_real(id_contribution_area_dict[id])
            ]
            out_vector.add_attribute_record(field_data, deleted=False)

        #we also add the polygon area to the vector, the column name will be fixed as AREA
        return self.wbe.polygon_area(out_vector)

#endregion

    def repair_subbasin_and_assign_subbasin_id_contribution_area_to_sturcture(self, subbasin_raster:Raster, flow_acc_raster:Raster):
        """
        it modifies both subbasin and structure raster. 
        this has been used on wetland, feedlot and dugout

        replace repairSubbasinWithFlowDirChangeBMP
        """

        rows = self.boundary_raster.configs.rows
        cols = self.boundary_raster.configs.columns
        structure_raster_no_data = self.boundary_raster.configs.nodata
        subbasin_raster_no_data = subbasin_raster.configs.nodata
        mask_raster_no_data = self.__dem_raster.configs.nodata
        outlet_raster_node_data = self.outlet_raster.configs.nodata
        cell_size_ha = self.__dem_raster.configs.resolution_x * self.__dem_raster.configs.resolution_y / 10000.0

        #assuming 1:1 relationship from wetland to subbasin
        bmp2sub = {}
        bmp_contribute_area = {}
        for row in range(rows):
            for col in range(cols):
                wet_id = self.boundary_raster[row, col]
                sub_id = subbasin_raster[row, col]
                if wet_id != structure_raster_no_data and sub_id != subbasin_raster_no_data:
                    if int(wet_id) not in bmp2sub:
                        bmp2sub[int(wet_id)] = int(sub_id)

                    #get structure contribution area at the outlet    
                    if self.outlet_raster[row, col] != outlet_raster_node_data:
                        bmp_contribute_area[int(wet_id)] = flow_acc_raster[row, col] * cell_size_ha

        # Repair subbasin layer for the nodata cells within wetlands
        for row in range(rows):
            for col in range(cols):
                wet_id = self.boundary_raster[row, col]
                sub_id = subbasin_raster[row, col]
                if (sub_id == subbasin_raster_no_data and 
                    wet_id != structure_raster_no_data and 
                    self.__dem_raster[row, col] != mask_raster_no_data and 
                    int(wet_id) in bmp2sub):
                    subbasin_raster[row, col] = bmp2sub[int(wet_id)]

        # Remove wetlands that are not overlapping with subbasins
        for row in range(rows):
            for col in range(cols):
                if subbasin_raster[row, col] < 0:
                    self.boundary_raster[row, col] = structure_raster_no_data

        #save the change to file
        self.save_raster(self.boundary_raster, self.__structure_boundary_processed_raster_name)

        #assign subbasin id and contribution area to the shapefile also remove the structure that are not included in subbasin    
        processed_boundary_vector = self.__creatd_processed_boundary_vector(bmp2sub,bmp_contribute_area)
        self.save_vector(processed_boundary_vector, self.__structure_boundary_processed_vector_name)


#region Zhangbin - Not used anymore

    def __find_outlets_zhangbin(self):
        """
        1）首先找到湿地边界，寻找汇流累积量最大的3个cell，作为出口；
        对于其他流出的cell，强制流向湿地内；
        2）追溯每块湿地的上游
        :param structure_raster:  Raster of wetlands
        :param acc_threshold:   Threshold of accumulation,which is used to judge if the cell of extent can be the outlet

        Replace plugin WetlandOutletsPFO
        """ 
        
        #this is the ERSI pointer, different from the Whitebox pointer
        #dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        #dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}    

        #this is the whitebox direction
        dmove = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
        dmove_dic = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)} 

        structure_raster = self.boundary_original_raster
        dem_raster = self.__dem_raster
        acc_threshold = self.__structure_acc_theshold
        area_threshold = self.__structure_area_threshold_ha * 10000

        #generate flow dir and flow accumulation
        flow_dir_raster = self.wbe.d8_pointer(dem = dem_raster)
        flow_acc_raster = self.wbe.d8_flow_accum(raster = flow_dir_raster, input_is_pointer = True)

        #some processing here
        wetland_nodata = structure_raster.configs.nodata
        cell_area = structure_raster.configs.resolution_x * structure_raster.configs.resolution_y
        row = structure_raster.configs.rows
        col = structure_raster.configs.columns

        Vis = np.zeros((row, col))
        Result = np.zeros((row, col))
        Result[:, :] = wetland_nodata
        Vis1 = np.zeros((row, col))
        Vis2 = np.zeros((row, col))
        id = 1
        wetland_extent = np.zeros((row, col))
        wetland_extent[:, :] = wetland_nodata  #边界标记为1
        OUTLET = np.zeros((row, col))
        OUTLET[:, :] = wetland_nodata

        WETLAND = np.zeros((row, col)) #重新编码后的wetland
        for i in range(row):
            for j in range(col):
                WETLAND[i,j] = structure_raster[i,j]

        out = np.zeros((row, col))
        out[:, :] = wetland_nodata

        removed_wetland_ids = []
        removed_wetland_ids.append(wetland_nodata)

        for i in range(row):
            for j in range(col):
                if structure_raster[i, j] != wetland_nodata:
                    # print(id)
                    now_wetland_id = structure_raster[i, j]
                    extent = [] #边界栅格和其对应的FLOW ACC
                    wetland_cells = []
                    Wetland_Area = 0
                    if Vis[i, j] == 0:
                        # 搜索邻域内湿地并标记边界栅格
                        pop_cells = [(i, j)]  # 迭代列表
                        Vis[i, j] = 1  # 标记已遍历
                        temp_A = [] #属于同一个structure的所有cell的row and col index
                        while pop_cells:
                            pop_cell = pop_cells.pop()
                            wetland_cells.append(pop_cell)
                            temp_A.append(pop_cell)
                            Wetland_Area += cell_area
                            # 搜索8邻域内cell
                            flag = False
                            for k in range(8):
                                next_cell = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])
                                if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                    # if wetland[next_cell[0], next_cell[1]] != wetland[pop_cell[0], pop_cell[1]]:
                                    #     flag = True

                                    if Vis[next_cell[0], next_cell[1]] == 0 and structure_raster[next_cell[0], next_cell[1]] == \
                                            structure_raster[i, j]:
                                        pop_cells.append(next_cell)
                                        Vis[next_cell[0], next_cell[1]] = 1

                        # 判断是否为边界栅格
                        for cell in temp_A:
                            for k in range(8):
                                next_cell = (cell[0] + dmove[k][0], cell[1] + dmove[k][1])
                                if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                    if structure_raster[next_cell[0], next_cell[1]] != structure_raster[i, j]:
                                        extent.append((cell[0], cell[1], flow_acc_raster[cell[0], cell[1]]))
                                        break
                                else:
                                    extent.append((cell[0], cell[1], flow_acc_raster[cell[0], cell[1]]))
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
                        if temp_num >= self.__structure_split_max_num:
                            break
                        # 先判断是否流出，再判断Acc阈值
                        now_dir = flow_dir_raster[extent[ii][0], extent[ii][1]]
                        if now_dir in dmove_dic:
                            #找到下游的cell
                            ds_cell = (extent[ii][0] + dmove_dic[now_dir][0], extent[ii][1] + dmove_dic[now_dir][1])
                            if 0 <= ds_cell[0] < row and 0 <= ds_cell[1] < col:
                                #向外流出的cell
                                if structure_raster[ds_cell[0], ds_cell[1]] != structure_raster[extent[ii][0], extent[ii][1]]:
                                    out[extent[ii][0], extent[ii][1]] = 2
                                    # 流向湿地外，判断Acc阈值
                                    # 只有超过一定的阙值才会作为出口
                                    if extent[ii][2] >= acc_threshold:
                                        #出口的位置和Acc
                                        outlets.append(extent[ii])

                                        #标记出口位置
                                        OUTLET[extent[ii][0], extent[ii][1]] = 1
                                        temp_num += 1
                    #去掉面积太小的
                    if Wetland_Area <= area_threshold:
                        removed_wetland_ids.append(now_wetland_id)
                        for cell in outlets[1:]:
                            outlets.remove(cell)
                            OUTLET[cell[0], cell[1]] = wetland_nodata

                        #if the wetland is removed, there is no need to process it further
                        continue

                    # 如果面积小于阈值则outlets==[]，此时说明湿地没有流向外面的cell，则以SEIMS方式处理
                    # print(outlets)
                    if len(outlets) == 0:
                        # print('**')
                        # outlets=extent.copy()
                        # outlets=wetland_cells.copy()
                        Method = 2

                    if Method == 2:
                        # SEIMS:按照湿地边界追溯上游
                        # 边界内的所有CELL
                        cells = wetland_cells.copy()
                        # print(cells)
                        # print(extent)
                        while cells:
                            cell = cells.pop()
                            Result[cell[0], cell[1]] = id #wetland重新编号
                            Us_cells = self.__get_upstream_cell(flow_dir_raster, cell[0], cell[1])
                            for temp_cell in Us_cells:
                                if Vis1[temp_cell[0], temp_cell[1]] == 0:
                                    if structure_raster[temp_cell[0], temp_cell[1]] == wetland_nodata:
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
                                                flow_acc_raster[next_cell_1[0], next_cell_1[1]])
                                    #just process the cells at the boundary
                                    if wetland_extent[next_cell[0], next_cell[1]] == 1:
                                        # 如果是下游是流出湿地，则纠正流向
                                        next_cell_dir = flow_dir_raster[next_cell[0], next_cell[1]]
                                        if next_cell_dir in dmove_dic:
                                            temp_next_cell = (next_cell[0] + dmove_dic[next_cell_dir][0],
                                                            next_cell[1] + dmove_dic[next_cell_dir][1])
                                            if 0 <= temp_next_cell[0] < row and 0 <= temp_next_cell[1] < col:
                                                if structure_raster[temp_next_cell[0], temp_next_cell[1]] != structure_raster[
                                                    next_cell[0], next_cell[1]]:
                                                    flow_dir_raster[next_cell[0], next_cell[1]] = 2 ** ((k + 4) % 8)
                                            wetland_extent[next_cell[0], next_cell[1]] = 2
                                            pop_cells.insert(0, next_cell)

                        # 3、追溯wetland上游并对分割后的wetland重新编码
                        for cell in outlets:
                            Vis9 = np.zeros((row, col))
                            cells = [cell]
                            Vis9[cell[0], cell[1]] = 1
                            while cells:
                                pop_cell = cells.pop()
                                Result[pop_cell[0], pop_cell[1]] = id
                                Us_cells = self.__get_upstream_cell(flow_dir_raster, pop_cell[0], pop_cell[1])
                                for temp_cell in Us_cells:
                                    if Vis9[temp_cell[0], temp_cell[1]] == 0:
                                        if structure_raster[temp_cell[0], temp_cell[1]] == wetland_nodata or structure_raster[
                                            temp_cell[0], temp_cell[1]] == now_wetland_id:
                                            cells.append(temp_cell)
                                            Vis9[temp_cell[0], temp_cell[1]] = 1
                            id += 1

        # 重构湿地
        Vis1[:, :] = 0
        second = {}
        for i in range(row):
            for j in range(col):
                if structure_raster[i, j] != wetland_nodata and structure_raster[i, j] not in removed_wetland_ids and Result[i, j] == wetland_nodata:
                    # 分割湿地后，有些湿地没有出口，需要再追溯上游
                    second.setdefault(structure_raster[i, j], []).append((i, j))

        for wet_ in second:
            wetland_cells = second[wet_]

            while wetland_cells:
                pop_cell = wetland_cells.pop()
                Result[pop_cell[0], pop_cell[1]] = id
                Us_cells = self.__get_upstream_cell(flow_dir_raster, pop_cell[0], pop_cell[1])
                for temp_cell in Us_cells:
                    if Vis1[temp_cell[0], temp_cell[1]] == 0:
                        if structure_raster[temp_cell[0], temp_cell[1]] == wetland_nodata or structure_raster[
                            temp_cell[0], temp_cell[1]] == wet_:
                            wetland_cells.append(temp_cell)
                            Vis1[temp_cell[0], temp_cell[1]] = 1
            id += 1

        # 重构编码
        us = {}
        for i in range(row):
            for j in range(col):
                if Result[i, j] != wetland_nodata:
                    us.setdefault(Result[i, j], []).append((i, j))
        
        #再一次重新编码，确保从1开始
        Result[:, :] = wetland_nodata
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
                if OUTLET[i,j] != wetland_nodata:
                    OUTLET[i,j] = Result[i, j]

        #create rasters
        out_configs = structure_raster.configs
        out_configs.data_type = RasterDataType.F32

        wetland_extent_raster = self.wbe.new_raster(out_configs)
        wetland_upstream_raster = self.wbe.new_raster(out_configs)
        wetland_outlet_raster = self.wbe.new_raster(out_configs)
        wetland_modified_raster = self.wbe.new_raster(structure_raster.configs)
        wetland_out_raster = self.wbe.new_raster(out_configs)

        for i in range(row):
            for j in range(col):
                wetland_extent_raster[i,j] = wetland_extent[i,j]
                wetland_upstream_raster[i,j] = Result[i,j]
                wetland_outlet_raster[i,j] = OUTLET[i,j]
                wetland_modified_raster[i,j] = WETLAND[i,j]
                wetland_out_raster[i,j] = out[i,j]

        # 输出结果
        #return wetland_upstream_raster, wetland_extent_raster, wetland_outlet_raster, wetland_modified_raster, flow_dir_raster, wetland_out_raster
        return wetland_outlet_raster, wetland_modified_raster
    
    def __get_upstream_cell(self, flow_dir_raster:Raster, row:int, col:int):
        """
        查询输入栅格的上游栅格
        :param dir: array of dir
        :param row: row of the cell
        :param col:
        :return: [(i,j),(),]
        """
        #this is the ERSI pointer, different from the Whitebox pointer
        #dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        #dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}    

        #this is the whitebox direction
        dmove = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
        dmove_dic = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)} 

        up_cell = []
        row_num = flow_dir_raster.configs.rows
        col_num = flow_dir_raster.configs.columns

        for i in range(8):
            now_loc = (row + dmove[i][0], col + dmove[i][1])
            # print(now_loc)
            if 0 <= now_loc[0]<row_num and 0 <= now_loc[1]<col_num:
                if flow_dir_raster[now_loc[0], now_loc[1]] == 2 ** ((i + 4) % 8):
                    up_cell.append(now_loc)

        return up_cell

    def __find_flow_path(self, structure_raster, structure_outlet_raster, flow_dir_raster, structure_upstream_raster):
        """
        Build the flow path within the wetlands.

        :param OutLet: Outlets of wetlands
        :param Dir: Flow direction
        :param Wetland: Raster of the wetlands
        :param LS: Output result, Upstream of the wetlands
        :param nodata: Nodata of the Wetland
        :return:
        """
        #this is the ERSI pointer, different from the Whitebox pointer
        #dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        #dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}    

        #this is the whitebox direction
        dmove = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
        dmove_dic = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)} 

        row = structure_raster.configs.rows
        col = structure_raster.configs.columns
        wetland_nodata = structure_raster.configs.nodata

        Done = np.zeros((row, col))
        Vis = np.zeros((row, col))

        flow_tree = {}
        wbe = WbEnvironment()
        out_configs = structure_raster.configs
        out_configs.data_type = RasterDataType.I8
        out_configs.nodata = 0
        wetland_flowpath_raster = wbe.new_raster(structure_raster.configs)

        for i in range(row):
            for j in range(col):
                if structure_outlet_raster[i, j] != -9999:
                    # 找到出口，开始寻找下游
                    pop_cells = [(i, j)]
                    temp_road = [(i, j)]
                    # Vis[i, j] = 1
                    next_wetland_id = -1  # 没有下游湿地（流向边界外的或者洼地）为-1
                    now_wetland_id = structure_upstream_raster[i, j]
                    while pop_cells:
                        pop_cell = pop_cells.pop()
                        # print(pop_cell)
                        now_dir = flow_dir_raster[pop_cell[0], pop_cell[1]]
                        if now_dir in dmove_dic:
                            next_cell = (pop_cell[0] + dmove_dic[now_dir][0], pop_cell[1] + dmove_dic[now_dir][1])
                            if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:
                                if Vis[next_cell[0], next_cell[1]] == 0:
                                    if structure_raster[next_cell[0], next_cell[1]] != wetland_nodata and structure_raster[next_cell[0], next_cell[1]] != now_wetland_id:
                                        next_wetland_id = structure_upstream_raster[next_cell[0], next_cell[1]]
                                        if structure_outlet_raster[next_cell[0], next_cell[1]] != -9999:
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
                        wetland_flowpath_raster[cell[0], cell[1]] = 1
                    flow_tree.setdefault(structure_raster[i, j], set()).add(next_wetland_id)

        return flow_tree, wetland_flowpath_raster    

    def generate_flow_direction_raster_zhangbin(self)->Raster:
        """
        change the flow direction so it flows to the outlet at each structure. 

        it assumes there is only one outlet for each structure. The id doesn't matter here.
        """

        #this is the ERSI pointer, different from the Whitebox pointer
        #dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        #dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}    

        #this is the whitebox direction
        dmove = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
        dmove_dic = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)} 

        structure_raster = self.boundary_original_raster        
        outlet_raster = self.outlet_original_raster
        dem_raster = self.__dem_raster

        outlet_raster_no_data = outlet_raster.configs.nodata
   
        #generate original flow direction from dem
        flow_dir_raster = self.wbe.d8_pointer(dem = dem_raster)

        #get structure basic data
        wetland_nodata = structure_raster.configs.nodata
        cell_area = structure_raster.configs.resolution_x * structure_raster.configs.resolution_y
        row = structure_raster.configs.rows
        col = structure_raster.configs.columns

        Vis = np.zeros((row, col))              #search flag
        wetland_extent = np.zeros((row, col))
        wetland_extent[:, :] = wetland_nodata  #边界标记为1,出口标记为2

        for i in range(row):
            for j in range(col):
                if structure_raster[i, j] != wetland_nodata:
                    # print(id)
                    extent = [] #边界cell
                    wetland_cells = []
                    Wetland_Area = 0
                    outlets = []#出口cell,outlets is in extent

                    if Vis[i, j] == 0:
                        # 搜索邻域内湿地并标记边界栅格
                        pop_cells = [(i, j)]  # 迭代列表
                        Vis[i, j] = 1  # 标记已遍历
                        temp_A = [] #属于同一个structure的所有cell的row and col index
                        while pop_cells:
                            pop_cell = pop_cells.pop()
                            wetland_cells.append(pop_cell)
                            temp_A.append(pop_cell)
                            Wetland_Area += cell_area
                            # 搜索8邻域内cell
                            flag = False
                            for k in range(8):
                                next_cell = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])
                                if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                    if Vis[next_cell[0], next_cell[1]] == 0 and structure_raster[next_cell[0], next_cell[1]] == \
                                            structure_raster[i, j]:
                                        pop_cells.append(next_cell)
                                        Vis[next_cell[0], next_cell[1]] = 1

                        # 判断是否为边界栅格
                        for cell in temp_A:
                            for k in range(8):
                                next_cell = (cell[0] + dmove[k][0], cell[1] + dmove[k][1])
                                if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                    if structure_raster[next_cell[0], next_cell[1]] != structure_raster[i, j]:
                                        extent.append((cell[0], cell[1]))

                                        if outlet_raster[cell[0], cell[1]] != outlet_raster_no_data:
                                            outlets.append(extent[-1])
                                        break
                                else:
                                    extent.append((cell[0], cell[1]))
                                    if outlet_raster[cell[0], cell[1]] != outlet_raster_no_data:
                                            outlets.append(extent[-1])
                                            
                                    break
                    for cell in extent:
                        wetland_extent[cell[0], cell[1]] = 1

                    if len(outlets) > 0:
                        pop_cells = outlets.copy()  # 迭代列表
                        # print(pop_cells)
                        for cell_1 in outlets:
                            wetland_extent[cell_1[0], cell_1[1]] = 2

                        #保证所有的边界cell都指向出口
                        while pop_cells:
                            pop_cell = pop_cells.pop()
                            # print(pop_cell)
                            for k in range(8):
                                next_cell_1 = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])  # 临时变量
                                if 0 <= next_cell_1[0] < row and 0 <= next_cell_1[1] < col:  # 保证cell有效
                                    next_cell = (pop_cell[0] + dmove[k][0], pop_cell[1] + dmove[k][1])
                                    #just process the cells at the boundary
                                    if wetland_extent[next_cell[0], next_cell[1]] == 1:
                                        # 如果是下游是流出湿地，则纠正流向
                                        next_cell_dir = flow_dir_raster[next_cell[0], next_cell[1]]
                                        if next_cell_dir in dmove_dic:
                                            temp_next_cell = (next_cell[0] + dmove_dic[next_cell_dir][0],
                                                            next_cell[1] + dmove_dic[next_cell_dir][1])
                                            if 0 <= temp_next_cell[0] < row and 0 <= temp_next_cell[1] < col:
                                                if structure_raster[temp_next_cell[0], temp_next_cell[1]] != structure_raster[
                                                    next_cell[0], next_cell[1]]:
                                                    flow_dir_raster[next_cell[0], next_cell[1]] = 2 ** ((k + 4) % 8)#指向上一个边界cell或出口
                                            wetland_extent[next_cell[0], next_cell[1]] = 2
                                            pop_cells.insert(0, next_cell)



        wetland_boarder_raster = self.wbe.new_raster(structure_raster.configs)
        for i in range(row):
            for j in range(col):
                wetland_boarder_raster[i,j] = wetland_extent[i,j]
        self.save_raster(wetland_boarder_raster, f"{self.structure_type}BoarderLine{Names.raster_extension}")   


        return flow_dir_raster

#endregion Shawn

#region Shawn

    def __find_outlets_shawn(self):
        """
        Find structure outlets based using PFO methods

        Replace Plugin WetlandOutletsPFO        
        """

        logger.info(f"Looking for {self.structure_type} outlets ...")

        dem_raster = self.__dem_raster
        structure_raster = self.boundary_original_raster
        allow_multiple_output = self.__structure_allow_multiple_outlets
        using_PFO = self.__structure_using_PFO

        col, row, colN, rowN = 0, 0, 0, 0
        n = 0
        z, zN = 0.0, 0.0
        isPit, isEdgeCell, flag = False, False, False
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        backLink = [5, 6, 7, 8, 1, 2, 3, 4]

        nodata = dem_raster.configs.nodata
        rows = dem_raster.configs.rows
        cols = dem_raster.configs.columns

        dem2D =  np.full((rows, cols), nodata)
        output = np.full((rows, cols), nodata)
        flowdir = np.zeros((rows, cols), dtype=np.int8)
        queue = []
        inQueue = np.zeros((rows, cols), dtype=bool)

        flatIndex = 0
        k = 0
        dir = 0
        x, y = 0, 0

        if using_PFO:
            for row in range(rows):
                for col in range(cols):
                    z = dem_raster[row, col]
                    dem2D[row, col] = z
                    flowdir[row, col] = 0
                    if z != nodata:
                        isPit = True
                        isEdgeCell = False
                        for n in range(8):
                            zN = dem_raster[row + dY[n], col + dX[n]]
                            if isPit and zN != nodata and zN < z:
                                isPit = False
                            elif zN == nodata:
                                isEdgeCell = True
                        if isPit and isEdgeCell:                            
                            heapq.heappush(queue, GridCell(row=row, col=col, z=z, flatIndex = 0, streamVal=True))
                            inQueue[row, col] = True

            while queue:
                gc = heapq.heappop(queue)
                logger.debug(f"Row: {gc.row}, Col: {gc.col}, z: {gc.z}, flatIndex: {gc.flatIndex}")                
                z = gc.z
                row = gc.row
                col = gc.col    
                flatIndex = gc.flatIndex

                for n in range(8):
                    rowN = row + dY[n]
                    colN = col + dX[n]
                    if rowN >= rows or colN >= cols or rowN < 0 or colN < 0:
                        continue
                    zN = dem2D[rowN, colN]
                    if zN != nodata and not inQueue[rowN, colN]:
                        flowdir[rowN, colN] = backLink[n]
                        k = 0
                        if zN == dem2D[row, col]:
                            k = flatIndex + 1                            
                        heapq.heappush(queue, GridCell(row=rowN, col=colN, z=zN, flatIndex = k, streamVal=True))
                        inQueue[rowN, colN] = True

                        if structure_raster[row, col] != structure_raster[rowN, colN]:
                            flag = True
                            x = colN
                            y = rowN
                            isReturn = False
                            while flag:
                                #find the downslope neighbour
                                dir = flowdir[y, x] - 1
                                if dir > 0:
                                    if dir > 7:
                                        return
                                    x += dX[dir]
                                    y += dY[dir]
                                    if structure_raster[y, x] > 0:
                                        if structure_raster[rowN, colN] == structure_raster[y, x]:
                                            isReturn = True
                                            flag = False
                                        else:
                                            isReturn = False
                                            flag = False
                                else:
                                    flag = False
                            if not isReturn:
                                output[rowN, colN] = structure_raster[rowN, colN]
        else:
            c = 0
            flow_direction_raster = self.wbe.d8_pointer(dem = dem_raster)
            for row in range(rows):
                for col in range(cols):
                    if flow_direction_raster[row, col] > 0 and structure_raster[row, col] > 0:
                        z = dem_raster[row, col]
                        dem2D[row, col] = z
                        dir = int(flow_direction_raster[row, col])
                        if dir > 0:
                            c = int(math.log(dir) / self.LnOf2)
                            if c > 7:
                                raise ValueError("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")
                                
                            rowN = row + dX[c]
                            colN = col + dY[c]
                            if structure_raster[row, col] != structure_raster[rowN, colN]:
                                flag = True
                                x = colN
                                y = rowN
                                isReturn = False
                                count = 0
                                while flag and count < 100:
                                    dir = int(flow_direction_raster[y, x])
                                    if dir > 0:
                                        c = int(math.log(dir) / self.LnOf2)
                                        if c > 7:
                                            raise ValueError("An unexpected value has been identified in the pointer image. This tool requires a pointer grid that has been created using either the D8 or Rho8 tools.")

                                        if structure_raster[y, x] > 0:
                                            if structure_raster[row, col] == structure_raster[y, x]:
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
                                    output[row, col] = structure_raster[row, col]

        #Group the outlets and use the lowest one as the outlet
        outputNew = np.full((rows, cols), nodata)
        if allow_multiple_output:
            register = {}
            registerReverse = np.full((rows, cols), int(nodata))
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

            for locs in register.values():
                elevMap = {}
                for loc in locs:
                    elevMap[dem_raster[loc[0], loc[1]]] = loc
                elev = list(elevMap.keys())
                elev.sort()
                lowest = elev[0]
                outputNew[elevMap[lowest][0], elevMap[lowest][1]] = output[elevMap[lowest][0], elevMap[lowest][1]]

            #For multiple outlets wetland, outlet flow to wetland will not be count
            wetlandOutlets = {}
            suspectCounts = {}
            suspects = []
            for row in range(rows):
                for col in range(cols):
                    if outputNew[row, col] > 0 and structure_raster[row, col] > 0:
                        id = int(structure_raster[row, col])
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
                            if structure_raster[rowN, colN] > 0:
                                loc = [row, col]
                                suspects.append(loc)
                                if id in suspectCounts:
                                    suspectCounts[id] += 1
                                else:
                                    suspectCounts[id] = 1

            for loc in suspects:
                id = int(structure_raster[loc[0], loc[1]])
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

            for locs in register.values():
                elevMap = {}
                for loc in locs:
                    elevMap[dem_raster[loc[0], loc[1]]] = loc
                elev = list(elevMap.keys())
                elev.sort()
                lowest = elev[0]
                outputNew[elevMap[lowest][0], elevMap[lowest][1]] = output[elevMap[lowest][0], elevMap[lowest][1]]

        structure_outlet_raster = self.wbe.new_raster(dem_raster.configs)
        for row in range(rows):
            for col in range(cols):
                z = dem2D[row, col]
                if z != nodata:
                    structure_outlet_raster[row, col] = outputNew[row, col]

        return structure_outlet_raster

    def __categorize_wetland(self,
                main_stream_buffer_raster:Raster = None
                ):
        """
        1. Filter wetland with given min area, 
        2. Separate wetlands that have multiple outlets if user provides the outlets
        3. Separate isolated wetlands and riparian wetland if main stream buffer is provided
        4. Remove outlets that doesn't fall in the wetland boundary.

        Not used, instead just use polygon area to filter

        Replace filterWetland method.
        """

        if self.structure_type != "wetland":
            return None, None, None, None
        
        wetland_raster = self.boundary_original_raster
        wetland_outlet_raster = self.outlet_original_raster

        cell_area = wetland_raster.configs.resolution_x * wetland_raster.configs.resolution_y
        rows = wetland_raster.configs.rows
        cols = wetland_raster.configs.columns
        min_wetland_area_m2 = self.__structure_area_threshold_ha * 10000
        nodata = wetland_raster.configs.nodata

        wet_pixels = {}
        wet_outlet_count = {}
        rip_wet = set()

        for row in range(rows):
            for col in range(cols):
                if wetland_raster[row, col] > 0:
                    wet_id = int(wetland_raster[row, col])

                    #get the number of cells for each wetland
                    wet_pixels[wet_id] = wet_pixels.setdefault(wet_id, 0) + 1

                    #get the number of outlets for each wetland
                    #this may have issues as the outlet may not be in the wetland polygon right now
                    if wetland_outlet_raster is not None and wetland_outlet_raster[row, col] > 0:
                        wet_outlet_count[wet_id] = wet_outlet_count.setdefault(wet_id, 0) +  1
                    
                    #if the wetland is in the buffer of the stream, add to the riparian buffer list
                    if main_stream_buffer_raster is not None and main_stream_buffer_raster[row, col] > 0 and wet_id not in rip_wet:
                        rip_wet.add(wet_id)

        #remove the wetland that is smaller than given threshold value
        #this may has problem the rasterized wetland area may be smaller or larger than the polygon area depending on the resolution.
        #filtering by golygo area is much more accurate. 
        for wet_id in list(wet_pixels.keys()):
            if wet_pixels[wet_id] * cell_area < min_wetland_area_m2:
                wet_pixels[wet_id] = 0.0

        #wetlands that exceeds the threashold area
        wetland_no_small_raster = self.wbe.new_raster(wetland_raster.configs)

        #wetlands that have multiple outlets
        wetland_no_small_multi_raster = None
        if wetland_outlet_raster is not None:
            wetland_no_small_multi_raster = self.wbe.new_raster(wetland_raster.configs)
        
        #riparian and isolated wetlands
        wetland_isolated_raster = None
        wetland_rip_raster = None
        if main_stream_buffer_raster is not None:
            wetland_isolated_raster = self.wbe.new_raster(wetland_raster.configs)
            wetland_rip_raster = self.wbe.new_raster(wetland_raster.configs)

        for row in range(rows):
            for col in range(cols):
                wet_id = int(wetland_raster[row, col])
                if wet_id > 0 and wet_pixels[wet_id] > 0:
                    #skip the wetland if wetland doesn't have an outlet in the outlet raster
                    if wetland_outlet_raster is not None and wet_id not in wet_outlet_count:
                        continue
                    
                    wetland_no_small_raster[row, col] = wet_id

                    if wetland_outlet_raster is not None and wet_outlet_count[wet_id] > 1:
                        wetland_no_small_multi_raster[row, col] = wet_id

                    if main_stream_buffer_raster is not None:
                        if wet_id in rip_wet:
                            wetland_rip_raster[row, col] = wet_id
                        else:
                            wetland_isolated_raster[row, col] = wet_id

                elif wetland_outlet_raster and wetland_outlet_raster[row, col] > 0 and (wet_id not in wet_pixels or wet_pixels[wet_id] == 0):
                    #remove wetland outlets that are not inside of wetland boundary
                    wetland_outlet_raster[row, col] = nodata

        return wetland_no_small_raster, wetland_no_small_multi_raster, wetland_rip_raster, wetland_isolated_raster

    def generate_flow_direction_raster_shawn(self,
                                             stream_raster:Raster = None,
                                             lowerThresholdArea = 0,
                                             upperThresholdArea = float('inf'),
                                             reference_flow_direction_raster:Raster = None):
        """
        Generates the flow direction raster

        Replace plugin WetlandDirection
        """

        logger.info("Creating flow direction based on dem and structures ...")

        dem_raster = self.__dem_raster
        structure_vector = self.boundary_original_vector
        structure_raster = self.boundary_original_raster
        structure_outlet_raster = self.outlet_original_raster  

        #outputs
        structure_with_multiple_outlets_raster = None                                   #structures that have multiple outlets as the area exceeds the maximum area
        structure_riparian_raster = None                                                #structures that closes to stream
        structure_kept_raster = self.wbe.new_raster(dem_raster.configs)                 #structures that are kept for analysis the area is smaller than the maximum area but larger than the minimum area
        structure_isolated_raster = self.wbe.new_raster(dem_raster.configs)              #structure_with_multiple_outlets_raster + structure_with_single_outlet_raster
        structure_removed_raster = self.wbe.new_raster(dem_raster.configs)               #structures that remove as the area is smaller than minimum area
        flow_direction_raster = self.wbe.new_raster(dem_raster.configs)                  #final flow direction raster

        col, row, colN, rowN =  0, 0, 0, 0
        dir, n = 0, 0
        z, zN, zTest, zN2, lowestNeighbour = 0.0, 0.0, 0.0, 0.0, 0.0
        isPit, isEdgeCell, isWetland, flag = False, False, False, False
        gc = None

        # /*
        #  * 7  8  1
        #  * 6  X  2
        #  * 5  4  3
        #  */
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        backLink = [5, 6, 7, 8, 1, 2, 3, 4]
        outPointer = [0, 1, 2, 4, 8, 16, 32, 64, 128]
        inflowingVals = [16, 32, 64, 128, 1, 2, 4, 8]

        nodata = dem_raster.configs.nodata
        rows = dem_raster.configs.rows
        cols = dem_raster.configs.columns
        nodata_wetland = structure_raster.configs.nodata

        wetlandID = np.full((rows, cols), -32768, dtype=np.int32)
        wetlandPosition = np.full((rows, cols), -32768, dtype=np.int32)
        wetlandEndNodes = np.zeros((rows, cols), dtype=bool)

        count = 0
        points = []
        startingPointInPart, endingPointInPart = 0, 0
        i = 0
        x1, y1, x2, y2 = 0, 0, 0, 0


        conflictWetlands = set()
        wetland_boarder_raster = self.wbe.new_raster(dem_raster.configs) 

        #go through all the vertexs along the boundary to find confict wetlands and wetland position. 
        for index in range(structure_vector.num_records):
            #let's use wetland id here
            recNum = int(structure_vector.get_attribute_value(index, self.__structure_polygon_vector_id_field_name).get_value_as_f64())
            points = structure_vector[index].points
            numPoints = len(points)
            partData = structure_vector[index].parts
            numParts = len(partData)
            for part in range(numParts):
                startingPointInPart = partData[part]
                if part < numParts - 1:
                    endingPointInPart = partData[part + 1]
                else:
                    endingPointInPart = numPoints
                n = 0
                for i in range(startingPointInPart, endingPointInPart - 1):
                    x1 = dem_raster.get_column_from_x(points[i].x)
                    y1 = dem_raster.get_row_from_y(points[i].y)

                    x2 = dem_raster.get_column_from_x(points[i+1].x)
                    y2 = dem_raster.get_row_from_y(points[i+1].y)

                    d = 0

                    dy = abs(y2 - y1)
                    dx = abs(x2 - x1)

                    dy2 = dy << 1
                    dx2 = dx << 1

                    ix = 1 if x1 < x2 else -1
                    iy = 1 if y1 < y2 else -1

                    if dy <= dx:
                        while True:
                            if dem_raster[y1, x1] != nodata:
                                if wetland_boarder_raster[y1, x1] > 0 and wetland_boarder_raster[y1, x1] != recNum:
                                    wetID = int(structure_raster[y1, x1])
                                    if wetID > 0 and wetID not in conflictWetlands:
                                        conflictWetlands.add(wetID)
                                        for n in range(8):
                                            rowN = y1 + dY[n]
                                            colN = x1 + dX[n]
                                            neighbourID = int(structure_raster[rowN, colN])
                                            if neighbourID > 0 and neighbourID != wetID:
                                                if neighbourID not in conflictWetlands:
                                                    conflictWetlands.add(neighbourID)
                                else:
                                    n += 1
                                    wetland_boarder_raster[y1, x1] = recNum
                                    wetlandPosition[y1, x1] = n
                            if x1 == x2:
                                break
                            x1 += ix
                            d += dy2
                            if d > dx:
                                y1 += iy
                                d -= dx2
                    else:
                        while True:
                            if dem_raster[y1, x1] != nodata:
                                if wetland_boarder_raster[y1, x1] > 0 and wetland_boarder_raster[y1, x1] != recNum:
                                    wetID = int(structure_raster[y1, x1])
                                    if wetID > 0 and wetID not in conflictWetlands:
                                        conflictWetlands.add(wetID)
                                        for n in range(8):
                                            rowN = y1 + dY[n]
                                            colN = x1 + dX[n]
                                            neighbourID = int(structure_raster[rowN, colN])
                                            if neighbourID > 0 and neighbourID != wetID:
                                                if neighbourID not in conflictWetlands:
                                                    conflictWetlands.add(neighbourID)
                                else:
                                    n += 1
                                    wetland_boarder_raster[y1, x1] = recNum
                                    wetlandPosition[y1, x1] = n
                            if y1 == y2:
                                break
                            y1 += iy
                            d += dx2
                            if d > dy:
                                x1 += ix
                                d -= dy2
        self.save_raster(wetland_boarder_raster, f"{self.structure_type}BoarderLine{Names.raster_extension}")      

        wetland_position_raster = self.wbe.new_raster(dem_raster.configs)
        for row in range(rows):
            for col in range(cols):
                wetland_position_raster[row, col] = wetlandPosition[row, col]
        self.save_raster(wetland_position_raster, f"{self.structure_type}BoarderVertexIndex{Names.raster_extension}")      

        confWetGroups = defaultdict(list)
        confWetIsAdded = {id: -1 for id in conflictWetlands}

        riparianWetlandIDs = set()
        riparianWetlandRemoveIDs = set()
        if stream_raster is None:
            logger.info("No stream provided, no riparian wetland found!")

        wetlandCount = {}#numbe of cells of each wetland
        nodataWet = structure_raster.configs.nodata
        counter = 0
        for row in range(rows):
            for col in range(cols):
                if wetlandID[row, col] == -32768 and dem_raster[row, col] != nodata and structure_raster[row, col] > 0:
                    id = int(structure_raster[row, col])
                    wetlandPix = wetlandCount.get(id, 0)
                    wetlandCount[id] = wetlandPix + 1
                    wetlandID[row, col] = id
                    if stream_raster is not None and stream_raster[row, col] > 0 and reference_flow_direction_raster is None and reference_flow_direction_raster[row, col] > 0:
                        counter = 0
                        for n in range(8):
                            rowN = row + dY[n]
                            colN = col + dX[n]
                            if stream_raster[rowN, colN] > 0 and reference_flow_direction_raster[rowN, colN] == inflowingVals[n]:
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
                            rowN = row + dY[n]
                            colN = col + dX[n]
                            neighbourID = int(structure_raster[rowN, colN])
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
                    if wetlandCount.get(id, 0) > pix:
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

        pixelArea = dem_raster.configs.resolution_x * dem_raster.configs.resolution_y
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

        
        if len(isoMultiOutWetlandID)>0:
            structure_with_multiple_outlets_raster = self.wbe.new_raster(dem_raster.configs)

            for row in range(rows):
                for col in range(cols):
                    if wetlandID[row, col] > 0 and wetlandID[row, col] in isoMultiOutWetlandID:
                        structure_with_multiple_outlets_raster[row, col] = int(wetlandID[row, col])
                    else:
                        structure_with_multiple_outlets_raster[row, col] = nodataWet
        else:
            logger.info("No wetland bigger than threshold!")


        
        if stream_raster is not None and len(riparianWetlandIDs) > 0:
            structure_riparian_raster = self.wbe.new_raster(dem_raster.configs)

            for row in range(rows):
                for col in range(cols):
                    if wetlandID[row, col] > 0 and wetlandID[row, col] in riparianWetlandIDs:
                        structure_riparian_raster[row, col] = int(wetlandID[row, col])
                    else:
                        structure_riparian_raster[row, col] =  nodataWet


        if structure_outlet_raster is None:
            logger.info("No end node file provided!")

        for row in range(rows):
            for col in range(cols):
                if wetlandID[row, col] > 0:
                    id = int(wetlandID[row, col])
                    if id in isoNoOutWetlandID:
                        wetlandID[row, col] = -32768
                    if structure_outlet_raster is None and id in isoMultiOutWetlandID:
                        wetlandID[row, col] = -32768

                    if id in iso1OutWetlandID:
                        structure_kept_raster[row, col] = id

                    if id not in isoNoOutWetlandID:
                        structure_removed_raster[row, col] = id

                    if id in iso1OutWetlandID or id in isoMultiOutWetlandID:
                        structure_isolated_raster[row, col] = id
                else:
                    structure_kept_raster[row, col] = nodataWet

        self.save_raster(structure_kept_raster, f"{self.structure_type}Kept{Names.raster_extension}")     
        #self.save_raster(structure_removed_raster, f"{self.structure_type}BoarderLine{Names.raster_extension}")     

        id, idN, position, positionN = 0, 0, 0, 0
        minNeighbour, maxNeighbour = 0, 0
        elevation, elevationN, minElevation, maxElevation = 0.0, 0.0, 0.0, 0.0

        #flag the outlet cell for each structure
        for row in range(rows):
            for col in range(cols):
                id = wetlandID[row, col]
                if id > 0:
                    #use outlet raster layer if it's available. This assumes the outlet is at the boarder of structure
                    #if not, find the outlet along the boarder
                    if structure_outlet_raster is not None:
                        if structure_outlet_raster[row, col] > 0:
                            wetlandEndNodes[row, col] = True
                    else:
                        position = wetlandPosition[row, col]
                        minNeighbour = position
                        maxNeighbour = position
                        for n in range(8):
                            rowN = row + dY[n]
                            colN = col + dX[n]
                            positionN = wetlandPosition[rowN, colN]
                            idN = wetlandID[rowN, colN]
                            if idN == id:
                                if positionN < minNeighbour:
                                    minNeighbour = positionN
                                if positionN > maxNeighbour:
                                    maxNeighbour = positionN
                        if minNeighbour == position or maxNeighbour == position:
                            wetlandEndNodes[row, col] = True

        #find cells that is pit and edge
        output = np.full((rows, cols), nodata, dtype=np.float32)
        flowdir = np.zeros((rows, cols), dtype=np.int8)
        queue = []
        inQueue = np.zeros((rows, cols), dtype=bool)

        for row in range(rows):
            for col in range(cols):
                z = dem_raster[row, col]
                output[row, col] = z
                flowdir[row, col] = 0
                if z != nodata:
                    isWetland = wetlandID[row, col] > 0
                    isPit = True
                    isEdgeCell = False
                    for n in range(8):
                        zN = dem_raster[row + dY[n], col + dX[n]]
                        if isPit and zN != nodata and zN < z:
                            isPit = False
                        elif zN == nodata:
                            isEdgeCell = True
                    if (isPit and isEdgeCell) or (isWetland and isEdgeCell):
                        heapq.heappush(queue,GridCell(row=row, col=col, z=z, flatIndex = 0, streamVal = (not isWetland)))
                        inQueue[row, col] = True

        pit_edge_wetland_flag_raster = self.wbe.new_raster(dem_raster.configs)
        for row in range(rows):
            for col in range(cols):
                pit_edge_wetland_flag_raster[row, col] = 1 if inQueue[row, col] else nodata
        self.save_raster(pit_edge_wetland_flag_raster, f"{self.structure_type}PitEdgeStructureFlag{Names.raster_extension}")

        flatIndex = 0
        k = 0
        linkIDValue, linkIDValueN = 0, 0
        while queue:
            gc = heapq.heappop(queue)
            #logger.info(f"Row: {gc.row}, Col: {gc.col}, streamVal: {gc.streamVal}, isWetland: {not gc.streamVal} z: {gc.z}, flatIndex: {gc.flatIndex}")
            row = gc.row
            col = gc.col
            flatIndex = gc.flatIndex
            linkIDValue = wetlandID[row, col]
            isWetland = linkIDValue > 0
            if linkIDValue > 0:
                # /* move upstream following the path of 
                #  *  minimum change in link position. Stop
                #  *  when the link id changes.
                #  */
                flag = True
                r = row
                j = col
                while flag:
                    indexOfNextCell = -1
                    minPosDiff = float('inf')
                    posDiff = 0
                    position = wetlandPosition[r, j]
                    for n in range(8):
                        rowN = r + dY[n]
                        colN = j + dX[n]
                        linkIDValueN = wetlandID[rowN, colN]                        
                        #if the neibour is on the boarder
                        if linkIDValueN == linkIDValue and not inQueue[rowN, colN] and wetlandPosition[rowN, colN] > 0:
                            positionN = wetlandPosition[rowN, colN]
                            posDiff = (positionN - position) * (positionN - position)
                            if posDiff < minPosDiff:
                                minPosDiff = posDiff
                                indexOfNextCell = n
                        elif linkIDValueN == -32768 or wetlandEndNodes[rowN, colN] or wetlandPosition[rowN, colN] < 0:
                            zN = output[rowN, colN]
                            if zN != nodata and not inQueue[rowN, colN]:
                                # it's a non-stream cell or a link end node and can be added to the queue
                                flowdir[rowN, colN] = backLink[n]
                                #logger.info(f"Row = {rowN}, Col = {colN}, n = {n}, flow dir = {flowdir[rowN, colN]}")
                                k = 0
                                if zN == output[row, col]:
                                    k = flatIndex + 1
                                heapq.heappush(queue,GridCell(row=rowN, col=colN, z=zN, flatIndex = k, streamVal = (not wetlandEndNodes[rowN, colN])))
                                inQueue[rowN, colN] = True
                    if indexOfNextCell > -1:
                        rowN = r + dY[indexOfNextCell]
                        colN = j + dX[indexOfNextCell]
                        flowdir[rowN, colN] = backLink[indexOfNextCell]
                        #logger.info(f"Row = {rowN}, Col = {colN}, n = {indexOfNextCell}, flow dir = {flowdir[rowN, colN]}")
                        inQueue[rowN, colN] = True
                        r = rowN
                        j = colN
                    else:
                        #there were no unvisited neighbours of the same link ID
                        flag = False
            else:
                for n in range(8):
                    rowN = row + dY[n]
                    colN = col + dX[n]
                    if rowN >= rows or colN >= cols or rowN < 0 or colN < 0:
                        continue
                    zN = output[rowN, colN]
                    if zN != nodata and not inQueue[rowN, colN]:
                        linkIDValueN = wetlandID[rowN, colN]
                        if linkIDValueN == -32768 or wetlandEndNodes[rowN, colN]:
                            # else it's a stream and not an end node and shouldn't be added to the queue.
                            flowdir[rowN, colN] = backLink[n]
                            #logger.info(f"Row = {rowN}, Col = {colN}, n = {n}, flow dir = {flowdir[rowN, colN]}")
                            k = 0
                            if zN == output[row, col]:
                                k = flatIndex + 1
                            heapq.heappush(queue,GridCell(row=rowN, col=colN, z=zN, flatIndex = k, streamVal = (not wetlandEndNodes[rowN, colN])))
                            inQueue[rowN, colN] = True
                    

        for row in range(rows):
            for col in range(cols):
                z = output[row, col]
                if z != nodata:
                    flow_direction_raster[row, col] = outPointer[flowdir[row, col]]

        return flow_direction_raster

#endregion
 

#region Offset Outlet

    def __offset_outlets(self)->Raster:
        """
        Snap the given outlets to the structure if necessary. 
        It assumes the outlet has the same id as the structure, which is very important.

        Translate from plugin: WetlandOutletsOffset
        """

        logger.info(f"Offseting user-defined {self.structure_type} outlets ...")

        structure_raster = self.boundary_original_raster
        structure_outlet_raster = self.outlet_original_raster
        dem_raster = self.__dem_raster

        structure_outlet_offset_raster = self.wbe.new_raster(structure_outlet_raster.configs)

        rows = structure_outlet_raster.configs.rows
        cols = structure_outlet_raster.configs.columns

        wetlandMap = {}
        for row in range(rows):
            for col in range(cols):
                if structure_raster[row, col] > 0:
                    id = int(structure_raster[row, col])
                    wetlandMap.setdefault(id,[]).append((row, col))

        for row in range(rows):
            for col in range(cols):
                if structure_outlet_raster[row, col] > 0:
                    id = int(structure_outlet_raster[row, col])
                    if id in wetlandMap:
                        if id == int(structure_raster[row, col]):
                            if self.__isEdgePoint((row, col), wetlandMap[id]):
                                #if it's just at the edge, then use it directly
                                structure_outlet_offset_raster[row, col] = id
                            else:
                                #if the outlet is not at the edge, then move it to the edge
                                outlet = self.__offsetInsidePointToEdge((row, col), wetlandMap[id], dem_raster)
                                structure_outlet_offset_raster[outlet[0], outlet[1]] = id
                        else:
                            #if not in the wetland polygon, then we will need to snap to the closet point
                            outlet = self.__getClosestPoint((row, col), wetlandMap[id])
                            structure_outlet_offset_raster[outlet[0], outlet[1]] = id

        return structure_outlet_offset_raster

    def __getClosestPoint(self, checkPoint, area):
        """
        Snap the outlet to the structure
        """

        distance = float('inf')
        index = 0
        for i in range(len(area)):
            d = (area[i][0] - checkPoint[0]) ** 2 + (area[i][1] - checkPoint[1]) ** 2
            if d < distance:
                distance = d
                index = i
            if distance <= 0:
                return area[i]
        return area[index]

    def __offsetInsidePointToEdge(self, checkPoint, area, dem_raster):
        """
        Offset inside points to edge
        """
        distance = float('inf')
        indexes = []

        for i in range(len(area)):
            if self.__isEdgePoint(area[i], area):
                d = (area[i][0] - checkPoint[0]) ** 2 + (area[i][1] - checkPoint[1]) ** 2
                if d < distance:
                    distance = d
                    indexes = [i]
                elif d == distance:
                    indexes.append(i)
                if distance <= 0:
                    break

        index = indexes[0]

        if len(indexes) > 1:
            elev = float('inf')
            for i in indexes:
                elevValue = dem_raster[area[i][0], area[i][1]]
                if elevValue < elev:
                    elev = elevValue
                    index = i

        return area[index]

    def __isEdgePoint(self, checkPoint, area):
        """
        Check if the point is at edge
        """
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]
        flag = False

        for c in range(8):
            x = checkPoint[1] + dX[c]
            y = checkPoint[0] + dY[c]
            flag = not (y, x) in area and (checkPoint[0], checkPoint[1]) in area
            if flag:
                break

        return flag


#endregion

@dataclass(order=True)
class GridCell:
    row: int = field(compare=False)
    col: int = field(compare=False)
    streamVal: bool 
    z: float
    flatIndex: int