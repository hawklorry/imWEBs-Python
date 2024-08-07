import networkx as nx
import numpy
import pandas as pd
import yaml
from whitebox_workflows import AttributeField, FieldData, FieldDataType, VectorGeometryType, WbEnvironment
# global variable
wbe = WbEnvironment()
UTIL_ZERO = 1.e-6
MINI_SLOPE = 0.0001
DEFAULT_NODATA = -9999.
SQ2 = 1.4142135623730951
PI = 3.141592653589793
FLD_LINKNO = 'LINKNO'
FLD_DSLINKNO = 'DSLINKNO'
REACH_WIDTH = 'WIDTH'
REACH_LENGTH = 'Length'
REACH_DEPTH = 'DEPTH'
DELTA = 1e-6

class reach:
    # Spatial parameters
    _TAB_REACH = 'REACHES'
    _LINKNO = 'LINKNO'
    _DSLINKNO = 'DSLINKNO'  # Fields in _TAB_REACH
    _SUBBASIN = 'SUBBASINID'
    _NUMCELLS = 'NUM_CELLS'
    _DOWNSTREAM = 'DOWNSTREAM'
    _WIDTH = 'CH_WIDTH'
    _LENGTH = 'CH_LEN'
    _DEPTH = 'CH_DEPTH'
    _WDRATIO = 'CH_WDRATIO'
    _AREA = 'CH_AREA'
    _SIDESLP = 'CH_SSLP'  # H/V. 0: vertical band, 5: bank with gentle side slope. chside in SWAT
    _SLOPE = 'CH_SLP'
    # Hydrological related parameters
    _MANNING = 'CH_N'  # Manning's "n" value
    _BEDK = 'CH_BED_K'  # effective hydraulic conductivity, mm/hr. In SWAT, only ch_k are provided.
    _BNKK = 'CH_BNK_K'
    # Erosion related parameters
    _BEDBD = 'CH_BED_BD'  # bulk density of channel bed sediment (1.1-1.9), g/cm^3
    _BNKBD = 'CH_BNK_BD'  # bulk density of channel bank sediment (1.1-1.9), g/cm^3
    _BEDCOV = 'CH_BED_COV'  # Channel bed cover factor (0-1), ch_cov2 in SWAT.
    _BNKCOV = 'CH_BNK_COV'  # Channel bank cover factor, ch_cov1 in SWAT.
    _BEDEROD = 'CH_BED_EROD'  # Erodibility of channel bed sediment, ch_bed_kd in SWAT(0.001 - 3.75)
    _BNKEROD = 'CH_BNK_EROD'  # Erodibility of channel bank sediment, ch_bnk_kd in SWAT (cm3/N-s)
    _BEDD50 = 'CH_BED_D50'  # D50(median) particle size diameter of channel bed sediment, micrometer
    _BNKD50 = 'CH_BNK_D50'  # D50(median) particle size diameter of channel bank sediment, 0.001-20
    # Nutrient routing related parameters
    _BC1 = 'BC1'
    _BC2 = 'BC2'
    _BC3 = 'BC3'
    _BC4 = 'BC4'
    _RK1 = 'RK1'
    _RK2 = 'RK2'
    _RK3 = 'RK3'
    _RK4 = 'RK4'
    _RS1 = 'RS1'
    _RS2 = 'RS2'
    _RS3 = 'RS3'
    _RS4 = 'RS4'
    _RS5 = 'RS5'
    _DISOX = 'DISOX'  # 0-50 mg/L
    _BOD = 'BOD'  # 0-1000 mg/L
    _ALGAE = 'ALGAE'  # 0-200 mg/L
    _ORGN = 'ORGN'  # 0-100 mg/L, ch_onco in SWAT
    _NH4 = 'NH4'  # 0-50 mg/L
    _NO2 = 'NO2'  # 0-100 mg/L
    _NO3 = 'NO3'  # 0-50 mg/L
    _ORGP = 'ORGP'  # 0-25 mg/L, ch_opco in SWAT
    _SOLP = 'SOLP'  # 0-25 mg/L
    # Groundwater nutrient related parameters
    _GWNO3 = 'GWNO3'  # 0-1000 mg/L
    _GWSOLP = 'GWSOLP'  # 0-1000 mg/L
    #by wanghaocheng
    _MINELEVATION="min_elev"
    _VELOCITY="VELOCITY"
    _MAXELEVATION="max_elev"
    _AVGELEVATION="avg_elev"
    _MINFLOW="minFlow"
    _k_chb="k_chb"
    _k_bank="k_bank"
    _bnk0="bnk0"
    _chs0="chs0"
    _a_bnk="a_bnk"
    _b_bnk="b_bnk"
    _MSK_X="MSK_X"
    _MSK_col="MSK_col"
    #by wanghaocheng
    def execute(self,filename):
        try:
            with open(filename, 'r') as file_obj:
                params = yaml.load(file_obj, Loader=yaml.FullLoader)
            #1、重新排列id
            self.redefine_id(params["stream_net_file"], params["out_reach_shp"])
            #2、加深度、宽度
            self.add_channel_width_depth_to_shp(params["out_reach_shp"], params["streamlink_file"],
                                                params["channel_width_file"],
                                                params["channel_depth_file"])
            #3、加高程、流速、order
            self.get_elevation_statistic(params["streamlink_file"], params["dem_file"], params["out_reach_shp"])
            self.get_velocity_statistic(params["streamlink_file"], params["velocity_file"], params["out_reach_shp"])
            self.get_Order_statistic(params["streamlink_file"], params["stream_order_file"], params["out_reach_shp"])
            #4、加流域参数，如流域栅格数、面积等
            dict=self.read_reach_dict(params["out_reach_shp"])
            dict=self.get_subbasin_cell_count(params["subbsn_file"], dict)
            #5、加流域上下游信息
            g = self.construct_flow_graph(dict)
            downup_order = self.construct_downup_order(g)
            updown_order = self.construct_updown_order(g)
            #6、加曼宁系数
            min_manning = 0.035
            max_manning = 0.075

            rch_orders = list(updown_order.values())
            min_order = min(rch_orders)
            max_order = max(rch_orders)

            a = (max_manning - min_manning) / (max_order - min_order)
            for tmpid in list(dict.keys()):
                dict[tmpid]['manning'] = max_manning - a * (updown_order[tmpid] - min_order)
            #7、导出结果
            data = self.import_reach_info(dict, updown_order, downup_order)
            data.to_csv(params["output_dir"] + "/output.csv")
            print()
        except Exception as e:
            # 这里处理异常情况
            print(f"An error occurred: {e}")
    def dealAttributeField(self,att_fields):
        att_fields1=[]
        for i in range(len(att_fields)):  # ...........................(无语)
            if att_fields[i].decimal_count == 0:
                att_fields1.append(AttributeField(att_fields[i].name, FieldDataType.Int, att_fields[i].field_length,
                                                  att_fields[i].decimal_count))
            else:
                att_fields1.append(
                    AttributeField(att_fields[i].name, FieldDataType.Real, att_fields[i].field_length,
                                   att_fields[i].decimal_count))
        return att_fields1
    def redefine_id(self, streamnet_file, output_reach_file):
        """Eliminate reach with zero length and return the reach ID map.
        Args:
            streamnet_file: original stream net ESRI shapefile
            output_reach_file: serialized stream net, ESRI shapefile

        Returns:
            id pairs {origin: newly assigned}
        """
        input_vector = wbe.read_vector(streamnet_file,)
        att_fields = input_vector.get_attribute_fields()#试下代码对不对
        att_fields1=self.dealAttributeField(att_fields)
        output_vector = wbe.new_vector(VectorGeometryType.PolyLine, att_fields1, proj=input_vector.projection)
        old_id_list = []
        output_dic = {}
        for i in range(input_vector.num_records):
            link_id =int (input_vector.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            reach_len =  input_vector.get_attribute_value(i, REACH_LENGTH).get_value_as_f64()
            if link_id not in old_id_list:
                if reach_len < DELTA:
                    downstream_id = input_vector.get_attribute_value(i, FLD_DSLINKNO)
                    output_dic[link_id] = downstream_id
                else:
                    old_id_list.append(link_id)
        old_id_list.sort()
        id_map = {}
        for i, old_id in enumerate(old_id_list):
            id_map[old_id] = i + 1
        # print(id_map)
        # change old ID to new ID
        for i in range(input_vector.num_records):
            link_id = int(input_vector.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            ds_id = int( input_vector.get_attribute_value(i, FLD_DSLINKNO).get_value_as_f64())
            ds_id = output_dic.get(ds_id, ds_id)
            ds_id = output_dic.get(ds_id, ds_id)
            geom = input_vector[i]
            output_vector.add_record(geom)
            att_rec = input_vector.get_attribute_record(i)# Add the record to the output Vector
            att_rec[0] = FieldData.new_int(id_map[link_id])
            if ds_id in id_map:
                att_rec[1] = FieldData.new_int(id_map[ds_id])
            else:
                att_rec[1] = FieldData.new_int(-1)
            output_vector.add_attribute_record(att_rec, deleted=False)
        wbe.write_vector(output_vector, output_reach_file)
        return id_map
    def get_elevation_statistic(self, stream_link,dem,reach_shp_file):
        # read steam_link dem to get elevation inforamtion of reach
        stream_link_raster = wbe.read_raster(stream_link)
        dem_raster = wbe.read_raster(dem)
        n_rows = stream_link_raster.configs.rows
        n_cols = stream_link_raster.configs.columns
        nodata_value = stream_link_raster.configs.nodata
        # output
        elevation_sum = {}
        elevation_avg = {}
        elevation_min = {}
        elevation_max = {}
        count = {}
        for i in range(n_rows):
            for j in range(n_cols):
                if abs(stream_link_raster[i,j] - nodata_value) <= UTIL_ZERO:
                    continue
                tmpid = int(stream_link_raster[i,j])
                # set_default
                elevation_sum.setdefault(tmpid, 0)
                count.setdefault(tmpid, 0)
                elevation_min.setdefault(tmpid, 999999)
                elevation_max.setdefault(tmpid, -999999)
                # calculate statistics
                elevation_sum[tmpid] += dem_raster[i,j]
                if (dem_raster[i,j] < elevation_min[tmpid]):
                    elevation_min[tmpid] = dem_raster[i,j]
                if (dem_raster[i,j] > elevation_max[tmpid]):
                    elevation_max[tmpid] = dem_raster[i,j]
                count[tmpid] += 1
        for key, value in count.items():
            elevation_avg[key] = elevation_sum[key] / count[key]

        # add ELEVATION statistic fields to reach shp file or update values if the fields exist
        ds_reach = wbe.read_vector(reach_shp_file)
        i_link = ds_reach.get_attribute_field_num(self._WIDTH)
        i_AVG = ds_reach.get_attribute_field_num(self._AVGELEVATION)
        i_MAX =ds_reach.get_attribute_field_num(self._MAXELEVATION)
        i_MIN = ds_reach.get_attribute_field_num(self._MINELEVATION)
        fieldlist=ds_reach.get_attribute_fields()
        if i_AVG is None:
            new_field = AttributeField(self._AVGELEVATION, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        if i_MAX is None:
            new_field = AttributeField(self._MAXELEVATION, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        if i_MIN is None:
            new_field = AttributeField(self._MINELEVATION, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        fieldlist1=self.dealAttributeField(fieldlist)
        out_reach = wbe.new_vector(VectorGeometryType.PolyLine, fieldlist1, proj=ds_reach.projection)
        for i in range(ds_reach.num_records):
            tmpid = int(ds_reach.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            a = 0
            b = 0
            c = 0
            if tmpid in elevation_max:
                a = elevation_max[tmpid]
            if tmpid in elevation_min:
                b = elevation_min[tmpid]
            if tmpid in elevation_avg:
                c = elevation_avg[tmpid]
            geom = ds_reach[i]
            out_reach.add_record(geom)
            att_rec = ds_reach.get_attribute_record(i)
            att_rec.append(FieldData.new_real(c))
            att_rec.append(FieldData.new_real(a))
            att_rec.append(FieldData.new_real(b))
            out_reach.add_attribute_record(att_rec, deleted=False)
        wbe.write_vector(out_reach, reach_shp_file)
    # 我其实不太确定imwebs的order是啥意思，这里是基于seims的河流order数据，并基于imwebs的Reach.java里的逻辑写的，要是和imwebs不一样的话，再联系我改
    def get_Order_statistic(self, stream_link, order, reach_shp_file):
        stream_link_raster = wbe.read_raster(stream_link)
        reachOrderRaster = wbe.read_raster(order)
        n_rows = stream_link_raster.configs.rows
        n_cols = stream_link_raster.configs.columns
        nodata_value = stream_link_raster.configs.nodata
        SubMax = int(stream_link_raster.configs.maximum)
        rchsum = [0]*SubMax
        rchcount = [0]*SubMax
        for i in range(n_rows):
            for j in range(n_cols):
                currentValue = reachOrderRaster[i, j]
                currentSub = stream_link_raster[i, j]
                if (currentValue >= 0 and currentSub >= 0 ) :
                    rchsum[int(currentSub - 1)] = int(currentValue)
        maxOrder =  int(reachOrderRaster.configs.maximum)
        k=1
        for i in range(maxOrder+1):
            for j in range(SubMax):
                if (rchsum[j] == i) :
                    rchcount[j] = k
                    k+=1
        ds_reach = wbe.read_vector(reach_shp_file)
        fieldlist = ds_reach.get_attribute_fields()
        i_order = ds_reach.get_attribute_field_num("order")
        if i_order is None:
            new_field = AttributeField("order", FieldDataType.Int, 6, 0)
            fieldlist.append(new_field)
        fieldlist1 = self.dealAttributeField(fieldlist)
        out_reach = wbe.new_vector(VectorGeometryType.PolyLine, fieldlist1, proj=ds_reach.projection)
        for i in range(ds_reach.num_records):
            tmpid = int(ds_reach.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            a = rchcount[tmpid-1]
            geom = ds_reach[i]
            out_reach.add_record(geom)
            att_rec = ds_reach.get_attribute_record(i)
            att_rec.append(FieldData.new_int(a))
            out_reach.add_attribute_record(att_rec, deleted=False)
        wbe.write_vector(out_reach, reach_shp_file)
        print()
    def get_velocity_statistic(self,stream_link,velocity,reach_shp_file):
        stream_link_raster = wbe.read_raster(stream_link)
        velocity_raster = wbe.read_raster(velocity)
        n_rows = stream_link_raster.configs.rows
        n_cols = stream_link_raster.configs.columns
        nodata_value = stream_link_raster.configs.nodata
        #output
        velocity_sum={}
        velocity_avg={}
        count= {}
        for i in range(n_rows):
            for j in range(n_cols):
                if abs(stream_link_raster[i,j] - nodata_value) <= UTIL_ZERO:
                    continue
                tmpid = int(stream_link_raster[i,j])
                # set_default
                velocity_sum.setdefault(tmpid, 0)
                count.setdefault(tmpid, 0)
                #calculate statistics
                velocity_sum[tmpid]+=velocity_raster[i,j]
                count[tmpid]+=1
        for key, value in count.items():
            velocity_avg[key]=velocity_sum[key]/count[key]
        # add VELOCITY fields to reach shp file or update values if the fields exist
        ds_reach = wbe.read_vector(reach_shp_file)
        fieldlist = ds_reach.get_attribute_fields()
        i_VELOCITY = ds_reach.get_attribute_field_num(self._VELOCITY)
        if i_VELOCITY is None:
            new_field = AttributeField(self._VELOCITY, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        fieldlist1 = self.dealAttributeField(fieldlist)
        out_reach = wbe.new_vector(VectorGeometryType.PolyLine, fieldlist1, proj=ds_reach.projection)
        for i in range(ds_reach.num_records):
            tmpid = int(ds_reach.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            a=0
            if tmpid in velocity_avg:
                a = velocity_avg[tmpid]
            geom = ds_reach[i]
            out_reach.add_record(geom)
            att_rec = ds_reach.get_attribute_record(i)
            att_rec.append(FieldData.new_real(a))
            out_reach.add_attribute_record(att_rec, deleted=False)
        wbe.write_vector(out_reach, reach_shp_file)
    def add_channel_width_depth_to_shp(self, out_reach_shp, streamlink_file, channel_width_file, channel_depth_file):
        """Calculate average channel width and depth, and add or modify the attribute table
             of reach.shp
          """
        stream_link = wbe.read_raster(streamlink_file)
        n_rows = stream_link.configs.rows
        n_cols = stream_link.configs.columns
        nodata_value = stream_link.configs.nodata
        width = wbe.read_raster(channel_width_file)
        depth = wbe.read_raster(channel_depth_file)

        ch_width_dic = dict()
        ch_depth_dic = dict()
        ch_num_dic = dict()

        for i in range(n_rows):
            for j in range(n_cols):
                if abs(stream_link[i,j] - nodata_value) <= UTIL_ZERO:
                    continue
                tmpid = int(stream_link[i,j])
                ch_num_dic.setdefault(tmpid, 0)
                ch_width_dic.setdefault(tmpid, 0)
                ch_depth_dic.setdefault(tmpid, 0)

                ch_num_dic[tmpid] += 1
                ch_width_dic[tmpid] += width[i,j]
                ch_depth_dic[tmpid] += depth[i,j]

        for k in ch_num_dic:
            ch_width_dic[k] /= ch_num_dic[k]
            ch_depth_dic[k] /= ch_num_dic[k]

        # add channel width and depth fields to reach shp file or update values if the fields exist
        ds_reach = wbe.read_vector(out_reach_shp)
        data=ds_reach.get_attribute_record(0)
        i_link = ds_reach.get_attribute_field_num(self._LINKNO)
        i_width = ds_reach.get_attribute_field_num(self._WIDTH)
        i_depth = ds_reach.get_attribute_field_num(self._DEPTH)
        fieldlist=ds_reach.get_attribute_fields()
        if i_width is None:
            new_field = AttributeField(self._WIDTH, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        if i_depth  is None:
            new_field =AttributeField(self._DEPTH, FieldDataType.Real, 6, 2)
            fieldlist.append(new_field)
        fieldlist1=self.dealAttributeField(fieldlist)
        out_reach = wbe.new_vector(VectorGeometryType.PolyLine, fieldlist1, proj=ds_reach.projection)
        for i in range(ds_reach.num_records):
            tmpid = int(ds_reach.get_attribute_value(i, FLD_LINKNO).get_value_as_f64())
            w = 5.
            d = 1.5
            if tmpid in ch_width_dic:
                w = ch_width_dic[tmpid]
            if tmpid in ch_depth_dic:
                d = ch_depth_dic[tmpid]
            geom = ds_reach[i]
            out_reach.add_record(geom)
            att_rec = ds_reach.get_attribute_record(i)
            att_rec.append(FieldData.new_real( w))
            att_rec.append(FieldData.new_real(d))
            out_reach.add_attribute_record(att_rec,deleted=False)
        wbe.write_vector(out_reach, out_reach_shp)
    def get_subbasin_cell_count(self,subbsn_file, subdict=None):
        """Get cell number of each subbasin.
        Args:
            subbsn_file: subbasin raster file.
            subdict: default is None

        Returns:
            subbasin cell count dict and cell width
        """
        wtsd_raster = wbe.read_raster(subbsn_file)
        data=[]
        for i in range(wtsd_raster.configs.rows):
            temp=[]
            for j in range(wtsd_raster.configs.columns):
                temp.append(wtsd_raster[i,j])
            data.append(temp)
        my_array = numpy.array(data)
        values, counts = numpy.unique(my_array, return_counts=True)
        if not subdict:
            subdict = dict()
        for v, c in zip(values, counts):
            if abs(v - wtsd_raster.configs.nodata) < UTIL_ZERO:
                continue
            subdict[int(v)][self._NUMCELLS] = int(c)
            subdict[int(v)][self._AREA] = int(c) * wtsd_raster.configs.resolution_x ** 2
        return subdict
    def construct_flow_graph(self,downstream_dict):
        g = nx.DiGraph()
        for from_id, info in downstream_dict.items():
            if info['downstream'] > 0:
                g.add_edge(from_id, info['downstream'])
        return g
    def read_reach_dict(self, reach_shp, is_taudem=True):
        # type: (AnyStr, bool) -> Dict[int, Dict[AnyStr, Union[int, float]]]
        """Read information of subbasin.
        Args:
            reach_shp: reach ESRI shapefile.
            is_taudem: is TauDEM or not, true is default.

        Returns:
            rch_dict: {stream ID: {'downstream': downstreamID,
                                   'depth': depth value,
                                   'slope': slope value,
                                   'width': width value,
                                   'length': length value}
                                  }
        """
        rch_dict = dict()

        ds_reach = wbe.read_vector(reach_shp)
        if not is_taudem:  # For ArcSWAT
            self._LINKNO = 'FROM_NODE'
            self._DSLINKNO = 'TO_NODE'
            self._SLOPE = 'Slo2'  # TauDEM: Slope (tan); ArcSWAT: Slo2 (100*tan)
            self._LENGTH = 'Len2'  # TauDEM: Length; ArcSWAT: Len2
        ifrom =ds_reach.get_attribute_field_num(self._LINKNO)
        ito = ds_reach.get_attribute_field_num(str(self._DSLINKNO))
        idph = ds_reach.get_attribute_field_num(str(self._DEPTH))
        islp =ds_reach.get_attribute_field_num(str('Slope'))
        iwth = ds_reach.get_attribute_field_num(str(self._WIDTH))
        ilen = ds_reach.get_attribute_field_num(str('Length'))
        # by wanghaocheng
        imax_elev = ds_reach.get_attribute_field_num(str(self._MAXELEVATION))
        imin_elev = ds_reach.get_attribute_field_num(str(self._MINELEVATION))
        iavg_elev = ds_reach.get_attribute_field_num(str(self._AVGELEVATION))
        i_velocity = ds_reach.get_attribute_field_num(str(self._VELOCITY))
        for i in range(ds_reach.num_records):
            nfrom = int(ds_reach.get_attribute_value(i, self._LINKNO).get_value_as_f64())
            nto = int(ds_reach.get_attribute_value(i, self._DSLINKNO).get_value_as_f64())
            rch_dict[nfrom] = {'downstream': nto,
                               'depth': ds_reach.get_attribute_value(i, self._DEPTH).get_value_as_f64() if idph > 0. else 1.5,
                               'slope':ds_reach.get_attribute_value(i, 'Slope').get_value_as_f64()
                               if islp > -1 and ds_reach.get_attribute_value(i, 'Slope').get_value_as_f64() > MINI_SLOPE
                               else MINI_SLOPE,
                               'width': ds_reach.get_attribute_value(i, self._WIDTH).get_value_as_f64()  if iwth > 0. else 5.,
                               'length':ds_reach.get_attribute_value(i, 'Length').get_value_as_f64() ,
                               'max_elev':ds_reach.get_attribute_value(i, self._MAXELEVATION).get_value_as_f64() ,
                               'min_elev': ds_reach.get_attribute_value(i, self._MINELEVATION).get_value_as_f64() ,
                               'avg_elev': ds_reach.get_attribute_value(i, self._AVGELEVATION).get_value_as_f64() ,
                               'velocity': ds_reach.get_attribute_value(i, self._VELOCITY).get_value_as_f64(),
                               'order': int(ds_reach.get_attribute_value(i, "order").get_value_as_f64()) }
        return rch_dict
    def construct_downup_order(self,g):
        """

        Returns:
            downstream_up_order_dic: from outlet up stream dict
            upstream_down_order_dic: from source down stream dict
        """
        # find outlet subbasin
        outlet = -1
        for node in g.nodes():
            if g.out_degree(node) == 0:
                outlet = node
        if outlet < 0:
            raise ValueError('Cannot find outlet subbasin ID, please check the '
                             'threshold for stream extraction!')
        print('outlet subbasin:%d' % outlet)

        # assign order from outlet to upstream subbasins from 1
        downstream_up_order_dic = dict()
        start_node = [outlet]
        order_num = 0
        while start_node:
            tmp = list()
            order_num += 1
            for snode in start_node:
                downstream_up_order_dic[snode] = order_num
                for in_nodes in g.in_edges(snode):
                    tmp.append(in_nodes[0])
            start_node = tmp[:]
        # order_num now is the maximum order number from outlet
        # reserve the order number
        for k, v in downstream_up_order_dic.items():
            downstream_up_order_dic[k] = order_num - v + 1
        return downstream_up_order_dic

    def construct_updown_order(self,graph):
        # assign order from the source subbasins
        g = graph.copy()
        upstream_down_order_dic = dict()
        order_num = 1
        nodelist = g.nodes()
        while len(nodelist) != 0:
            nodelist = g.nodes()
            del_list = list()
            for node in nodelist:
                if g.in_degree(node) == 0:
                    upstream_down_order_dic[node] = order_num
                    del_list.append(node)
            for item in del_list:
                g.remove_node(item)
            order_num += 1

        return upstream_down_order_dic

    def import_reach_info(self, rch, updown, downup):
        """import reach info"""
        data = []
        for subbsn_id, rchdata in rch.items():
            dic = dict()
            dic[self._SUBBASIN] = subbsn_id
            dic["outlet_id"] = subbsn_id
            dic['length'] = rchdata['length']
            dic['width'] = rchdata['width']
            dic["main_side_slope"] = 0.5
            dic["floodplain_side_slope"] = 0.2
            dic["w_ratio"] = 3.5
            dic["depth"] = rchdata['depth']
            dic["slope"] = rchdata['slope']
            dic["order"] = rchdata['order']
            dic['manning'] = rchdata['manning']
            dic['velocity'] = rchdata['velocity']
            dic["t0"] = 0
            dic["d0"] = 0
            dic['min_elev'] = rchdata['min_elev']
            dic['max_elev'] = rchdata['max_elev']
            dic['avg_elev'] = rchdata['avg_elev']
            dic["receive_reach_id"] = rchdata['downstream']
            dic["contribution_area"] = rchdata['CH_AREA']
            dic["erodibility_factor"]=0.18
            dic["cover_factor"] = 1
            dic[self._BC1] = 0.55
            dic[self._BC2] = 1.1
            dic[self._BC3] = 0.21
            dic[self._BC4] = 0.35
            dic[self._RK1] = 1.71
            dic[self._RK2] = 50
            dic[self._RK3] = 0.36
            dic[self._RK4] = 2
            dic[self._RS1] = 1
            dic[self._RS2] = 0.05
            dic[self._RS3] = 0.5
            dic[self._RS4] = 0.05
            dic[self._RS5] = 0.05
            dic[self._MINFLOW] = 0.0
            dic[self._k_chb] = 0
            dic[self._k_bank] = 0
            dic[self._bnk0] = 0
            dic[self._chs0] = 0
            dic[self._a_bnk] = 0.2
            dic[self._b_bnk] = 0.05
            dic[self._MSK_X] = 0
            dic[self._MSK_col] = 0

            data.append(dic)
        data1 = pd.DataFrame()

        for i in data:
            if isinstance(i, (dict, pd.Series)):  # 检查i是否为字典或Series，以便转换为DataFrame
                df_to_append = pd.DataFrame([i])  # 将字典或Series转换为单行DataFrame
            elif isinstance(i, pd.DataFrame):  # 如果i已经是DataFrame，则直接使用
                df_to_append = i
            else:
                raise ValueError("Unsupported data type. Expected dict, Series, or DataFrame.")

            if not data1.empty:  # 如果data1非空，则使用concat追加
                data1 = pd.concat([data1, df_to_append], ignore_index=True)
            else:  # 如果data1为空，则直接赋值
                data1 = df_to_append
        return data1
if __name__ == "__main__":
    r=reach()
    r.execute("index.yaml")
