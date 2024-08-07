import numpy as np
from ..names import Names
from whitebox_workflows import Raster, WbEnvironment, RasterDataType, Vector
from ..folder_base import FolderBase
from ..vector_extension import VectorExtension
import logging
logger = logging.getLogger(__name__)

class Structure(FolderBase):    
    """
    Structure processing to get the outlet and modified structure and flow direction. 
    This apply to wetland, Feedlot, Dugout, Catchbasin and Manure Storage

    A structure will have a boundary polygon shapefile and an optional outlet point shapefile. 
    """

    structure_types = ["wetland","feedlot","dugout", "catchbasin", "manure_storage"]
    structure_types_affection_flow_direction = ["wetland","feedlot"]

    dmove = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}    

    def __init__(self, structure_type:str, 
                 output_folder:str, 
                 dem_raster:Raster, 
                 structure_polygon_vector:Vector, 
                 structure_polygon_vector_id_field_name: str = "id",                 
                 structure_outlet_point_vector:Vector = None, 
                 structure_outlet_point_vector_id_field_name:str = "id",
                 structure_area_threshold_ha = 0, 
                 structure_split_max_num = 1,
                 structure_acc_threshold = 0):
        super().__init__(output_folder)

        self.structure_type = structure_type
        self.__structure_polygon_vector = structure_polygon_vector
        self.__structure_polygon_vector_id_field_name = structure_polygon_vector_id_field_name
        self.__structure_outlet_point_vector = structure_outlet_point_vector
        self.__structure_outlet_point_vector_id_field_name = structure_outlet_point_vector_id_field_name
        self.__dem_raster = dem_raster

        if self.__structure_polygon_vector is None:
            raise ValueError(f"{self.structure_type}: The structure polygon shapefile is empty.")
        if not VectorExtension.check_field_in_vector(self.__structure_polygon_vector, self.__structure_polygon_vector_id_field_name):
                raise ValueError(f"{self.structure_type}: The given id field {self.__structure_polygon_vector_id_field_name} doesn't exist in boundary shapefile.")

        if self.__structure_outlet_point_vector is not None:
            if self.__structure_outlet_point_vector_id_field_name is None:
                raise ValueError(f"{self.structure_type}: The outlet shapefile id field name is empty.")
            if not VectorExtension.check_field_in_vector(self.__structure_outlet_point_vector, self.__structure_outlet_point_vector_id_field_name):
                raise ValueError(f"{self.structure_type}: The given id field {self.__structure_outlet_point_vector_id_field_name} doesn't exist in outlet shapefile.")

        #area threshold lower that which the structures will be removed.
        self.__structure_area_threshold_ha = structure_area_threshold_ha

        #number of sub-structures that one structure will be split.
        #default 3 for wetland
        #defautl 1 for all other structures
        self.__structure_split_max_num = structure_split_max_num

        #the threshold of flow acc that will be consiered as outlet
        self.__structure_acc_theshold = structure_acc_threshold

        #output file name
        self.__structure_boundary_original_raster_name = f"{self.structure_type}BoundaryOriginal{Names.raster_extension}"
        self.__structure_boundary_processed_raster_name = f"{self.structure_type}BoundaryProcessed{Names.raster_extension}"
        self.__structure_outlet_original_raster_name = f"{self.structure_type}OutletOriginal{Names.raster_extension}"
        self.__structure_outlet_processed_raster_name = f"{self.structure_type}OutletProcessed{Names.raster_extension}"
        self.__structure_outlet_processed_vector_name = f"{self.structure_type}OutletProcessed{Names.shapefile_extension}"

    @property
    def boundary_original_raster(self):
        raster = self.get_raster(self.__structure_boundary_original_raster_name)
        
        if raster is None:
            logger.debug(f"Convert {self.structure_type} boundary from shapefile ({self.__structure_polygon_vector.file_name}) to raster ...")
            raster = self.wbe.vector_polygons_to_raster(self.__structure_polygon_vector, base_raster = self.__dem_raster, field_name = self.__structure_polygon_vector_id_field_name)
            self.save_raster(raster, self.__structure_boundary_original_raster_name)

        return raster
    
    @property
    def boundary_processed_raster(self)->Raster:
        outlet_processed_raster = self.outlet_processed_raster
        return self.get_raster(self.__structure_boundary_processed_raster_name)
    
    @property
    def boundary_raster(self)->Raster:
        if self.boundary_processed_raster is None:
            return self.boundary_original_raster
        
        return self.boundary_processed_raster
    
    @property
    def outlet_raster(self)->Raster:
        return self.outlet_processed_raster
    
    @property
    def outlet_vector(self)->Vector:
        vector = self.get_vector(self.__structure_outlet_processed_vector_name)

        if vector is None:
            vector = self.wbe.raster_to_vector_points(self.outlet_raster)
            self.save_vector(vector, self.__structure_outlet_processed_vector_name)

        return vector
    
    @property
    def outlet_original_raster(self)->Raster:      
        raster = self.get_raster(self.__structure_outlet_original_raster_name)        
        if raster is None and self.__structure_outlet_point_vector is not None:            
            logger.debug(f"Convert {self.structure_type} outlet from shapefile ({self.__structure_outlet_point_vector.file_name}) to raster ...")
            raster = self.wbe.vector_polygons_to_raster(self.__structure_outlet_point_vector, base_raster = self.__dem_raster, field_name = self.__structure_outlet_point_vector_id_field_name)
            self.save_raster(raster, self.__structure_outlet_original_raster_name)

        return raster

    @property
    def outlet_processed_raster(self):
        raster = self.get_raster(self.__structure_outlet_processed_raster_name)        

        if raster is None:
            if self.outlet_original_raster is not None:
                logger.debug(f"Offset user-defined {self.structure_type} outlets ...")
                raster = self.__offset_structure_outlets()
            else:
                logger.debug(f"Look for {self.structure_type} outlets ...")
                raster, modified_boundary_raster = self.__find_structure_outlets()
                self.save_raster(modified_boundary_raster, self.__structure_boundary_processed_raster_name)
            self.save_raster(raster,self.__structure_outlet_processed_raster_name)

        return raster

    def repair_subbasin(self, subbasin_raster:Raster):
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

        #assuming 1:1 relationship from wetland to subbasin
        bmp2sub = {}
        for row in range(rows):
            for col in range(cols):
                wet_id = self.boundary_raster[row, col]
                sub_id = subbasin_raster[row, col]
                if wet_id != structure_raster_no_data and sub_id != subbasin_raster_no_data and int(wet_id) not in bmp2sub:
                    bmp2sub[int(wet_id)] = int(sub_id)

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

    def reorder_after_subbasin(self, subbasin_raster:Raster):
        """
        reorder the structure

        replace reorderWetlandIDWithSubbasin
        """

        rows = self.boundary_raster.configs.rows
        cols = self.boundary_raster.configs.columns

        count = 0
        map = {}
        for row in range(rows):
            for col in range(cols):
                wet = int(self.boundary_raster[row, col])
                sub = int(subbasin_raster[row, col])
                if wet > 0 and sub > 0:
                    if sub not in map:
                        count += 1
                        map[sub] = count
                    self.boundary_raster[row, col] = map[sub]

        #save the change to file
        self.save_raster(self.boundary_raster, self.__structure_boundary_processed_raster_name)

    def filter_structure(self, 
                    wetland_raster:Raster,
                    main_stream_buffer_raster:Raster = None,
                    wetland_outlet_raster:Raster = None
                    ):
        """
        1. Filter wetland with given min area, 
        2. Separate wetlands that have multiple outlets if user provides the outlets
        3. Separate isolated wetlands and riparian wetland if main stream buffer is provided

        This method is not required any more as find_outlets functions has option to remove the wetlands that are smaller than threshoed area.

        This is only applied to wetland
        """

        if self.structure_type != "wetland":
            return None, None, None, None

        cell_area = wetland_raster.configs.resolution_x * wetland_raster.configs.resolution_y
        rows = wetland_raster.configs.rows
        cols = wetland_raster.configs.columns
        min_wetland_area_m2 = self.__wetland_area_threshold_ha * 10000
        nodata = wetland_raster.configs.nodata

        wet_pixels = {}
        wet_outlet_count = {}
        rip_wet = set()

        for row in range(rows):
            for col in range(cols):
                if wetland_raster[row, col] > 0:
                    wet_id = int(wetland_raster[row, col])
                    wet_pixels[wet_id] = wet_pixels.setdefault(wet_id, 0) + 1

                    if wetland_outlet_raster is not None and wetland_outlet_raster[row, col] > 0:
                        wet_outlet_count[wet_id] = wet_outlet_count.setdefault(wet_id, 0) +  1

                    if main_stream_buffer_raster is not None and main_stream_buffer_raster[row, col] > 0 and wet_id not in rip_wet:
                        rip_wet.add(wet_id)

        for wet_id in list(wet_pixels.keys()):
            if wet_pixels[wet_id] * cell_area < min_wetland_area_m2:
                wet_pixels[wet_id] = 0.0


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
                    wetland_outlet_raster[row, col] = nodata

        return wetland_no_small_raster, wetland_no_small_multi_raster, wetland_rip_raster, wetland_isolated_raster

    @staticmethod
    def get_flow_direction(structure_raster:Raster, outlet_raster:Raster, dem_raster:Raster)->Raster:
        """
        change the flow direction so it flows to the outlet at each structure. 

        it assumes there is only one outlet for each structure. The id doesn't matter here.
        """

        wbe = WbEnvironment()
        outlet_raster_no_data = outlet_raster.configs.nodata
   
        #generate origial flow direction from dem
        flow_dir_raster = wbe.d8_pointer(dem = dem_raster)

        #get structure basic data
        wetland_nodata = structure_raster.configs.nodata
        cell_area = structure_raster.configs.resolution_x * structure_raster.configs.resolution_y
        row = structure_raster.configs.rows
        col = structure_raster.configs.columns

        Vis = np.zeros((row, col))
        wetland_extent = np.zeros((row, col))
        wetland_extent[:, :] = -9999  #边界标记为1

        for i in range(row):
            for j in range(col):
                if structure_raster[i, j] != wetland_nodata:
                    # print(id)
                    extent = [] #
                    wetland_cells = []
                    Wetland_Area = 0
                    outlets = []

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
                                next_cell = (pop_cell[0] + Structure.dmove[k][0], pop_cell[1] + Structure.dmove[k][1])
                                if 0 <= next_cell[0] < row and 0 <= next_cell[1] < col:  # 保证cell有效
                                    if Vis[next_cell[0], next_cell[1]] == 0 and structure_raster[next_cell[0], next_cell[1]] == \
                                            structure_raster[i, j]:
                                        pop_cells.append(next_cell)
                                        Vis[next_cell[0], next_cell[1]] = 1

                        # 判断是否为边界栅格
                        for cell in temp_A:
                            for k in range(8):
                                next_cell = (cell[0] + Structure.dmove[k][0], cell[1] + Structure.dmove[k][1])
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
                        while pop_cells:
                            pop_cell = pop_cells.pop()
                            # print(pop_cell)
                            for k in range(8):
                                next_cell_1 = (pop_cell[0] + Structure.dmove[k][0], pop_cell[1] + Structure.dmove[k][1])  # 临时变量
                                if 0 <= next_cell_1[0] < row and 0 <= next_cell_1[1] < col:  # 保证cell有效
                                    next_cell = (pop_cell[0] + Structure.dmove[k][0], pop_cell[1] + Structure.dmove[k][1])
                                    #just process the cells at the boundary
                                    if wetland_extent[next_cell[0], next_cell[1]] == 1:
                                        # 如果是下游是流出湿地，则纠正流向
                                        next_cell_dir = flow_dir_raster[next_cell[0], next_cell[1]]
                                        if next_cell_dir in Structure.dmove_dic:
                                            temp_next_cell = (next_cell[0] + Structure.dmove_dic[next_cell_dir][0],
                                                            next_cell[1] + Structure.dmove_dic[next_cell_dir][1])
                                            if 0 <= temp_next_cell[0] < row and 0 <= temp_next_cell[1] < col:
                                                if structure_raster[temp_next_cell[0], temp_next_cell[1]] != structure_raster[
                                                    next_cell[0], next_cell[1]]:
                                                    flow_dir_raster[next_cell[0], next_cell[1]] = 2 ** ((k + 4) % 8)
                                            wetland_extent[next_cell[0], next_cell[1]] = 2
                                            pop_cells.insert(0, next_cell)

        return flow_dir_raster

    def __find_structure_outlets(self):
        """
        1）首先找到湿地边界，寻找汇流累积量最大的3个cell，作为出口；
        对于其他流出的cell，强制流向湿地内；
        2）追溯每块湿地的上游
        :param structure_raster:  Raster of wetlands
        :param acc_threshold:   Threshold of accumulation,which is used to judge if the cell of extent can be the outlet

        Replace plugin WetlandOutletsPFO
        """

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
        Result[:, :] = -9999
        Vis1 = np.zeros((row, col))
        Vis2 = np.zeros((row, col))
        id = 1
        wetland_extent = np.zeros((row, col))
        wetland_extent[:, :] = -9999  #边界标记为1
        OUTLET = np.zeros((row, col))
        OUTLET[:, :] = -9999

        WETLAND = np.zeros((row, col)) #重新编码后的wetland
        for i in range(row):
            for j in range(col):
                WETLAND[i,j] = structure_raster[i,j]

        out = np.zeros((row, col))
        out[:, :] = -9999

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
                                next_cell = (pop_cell[0] + self.dmove[k][0], pop_cell[1] + self.dmove[k][1])
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
                                next_cell = (cell[0] + self.dmove[k][0], cell[1] + self.dmove[k][1])
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
                        if now_dir in self.dmove_dic:
                            #找到下游的cell
                            ds_cell = (extent[ii][0] + self.dmove_dic[now_dir][0], extent[ii][1] + self.dmove_dic[now_dir][1])
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
                        removed_wetland_ids.append[now_wetland_id]
                        for cell in outlets[1:]:
                            outlets.remove(cell)
                            OUTLET[cell[0], cell[1]] = -9999

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
                                next_cell_1 = (pop_cell[0] + self.dmove[k][0], pop_cell[1] + self.dmove[k][1])  # 临时变量
                                if 0 <= next_cell_1[0] < row and 0 <= next_cell_1[1] < col:  # 保证cell有效
                                    next_cell = (pop_cell[0] + self.dmove[k][0], pop_cell[1] + self.dmove[k][1],
                                                flow_acc_raster[next_cell_1[0], next_cell_1[1]])
                                    #just process the cells at the boundary
                                    if wetland_extent[next_cell[0], next_cell[1]] == 1:
                                        # 如果是下游是流出湿地，则纠正流向
                                        next_cell_dir = flow_dir_raster[next_cell[0], next_cell[1]]
                                        if next_cell_dir in self.dmove_dic:
                                            temp_next_cell = (next_cell[0] + self.dmove_dic[next_cell_dir][0],
                                                            next_cell[1] + self.dmove_dic[next_cell_dir][1])
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
                if structure_raster[i, j] != wetland_nodata and structure_raster[i, j] not in removed_wetland_ids and Result[i, j] == -9999:
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
                if Result[i, j] != -9999:
                    us.setdefault(Result[i, j], []).append((i, j))
        
        #再一次重新编码，确保从1开始
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
                if OUTLET[i,j] != -9999:
                    OUTLET[i,j] = Result[i, j]

        #create rasters
        out_configs = structure_raster.configs
        out_configs.data_type = RasterDataType.F32
        out_configs.nodata = -9999

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
                        if now_dir in self.dmove_dic:
                            next_cell = (pop_cell[0] + self.dmove_dic[now_dir][0], pop_cell[1] + self.dmove_dic[now_dir][1])
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

    def __offset_structure_outlets(self)->Raster:
        """
        Snap the given outlets to the structure if necessary. It assumes the outlet has the same id as the structure.

        Translate from plugin: WetlandOutletsOffset
        """

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
            if self.isEdgePoint(area[i], area):
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
    
    def __get_upstream_cell(self, flow_dir_raster:Raster, row:int, col:int):
        """
        查询输入栅格的上游栅格
        :param dir: array of dir
        :param row: row of the cell
        :param col:
        :return: [(i,j),(),]
        """
        up_cell = []
        row_num = flow_dir_raster.configs.rows
        col_num = flow_dir_raster.configs.columns

        for i in range(8):
            now_loc = (row + self.dmove[i][0], col + self.dmove[i][1])
            # print(now_loc)
            if 0 <= now_loc[0]<row_num and 0 <= now_loc[1]<col_num:
                if flow_dir_raster[now_loc[0], now_loc[1]] == 2 ** ((i + 4) % 8):
                    up_cell.append(now_loc)

        return up_cell
