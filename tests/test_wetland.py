from imWEBs.Interface.imWEBs.delineation.structure import Wetland
from whitebox_workflows import WbEnvironment, RasterDataType
import os

input_folder = r"C:\Work\imWEBs\Junzhi Liu\Zhangbin\Wetland\run_data\run_data"
output_folder = r"C:\Work\imWEBs\Junzhi Liu\Zhangbin\Wetland\run_data\Result_zhiqiang"

wbe = WbEnvironment()
wetland_raster = wbe.read_raster(os.path.join(input_folder,"wetland.tif"))
flow_dir_raster = wbe.read_raster(os.path.join(input_folder,"Dir.tif"))
flow_acc_raster = wbe.read_raster(os.path.join(input_folder,"Acc.tif"))

#test new raster
# out_configs = wetland_raster.configs
# out_configs.data_type = RasterDataType.F32
# out_configs.nodata = -9999
# wbe.write_raster(wbe.new_raster(out_configs), os.path.join(output_folder, "new_raster.tif"))

wetland = Wetland()
# wetland_upstream_raster, wetland_extent_raster, wetland_outlet_raster, wetland_modified_raster, flow_dir_raster, wetland_out_raster = wetland.find_outlets(wetland_raster, flow_dir_raster, flow_acc_raster)


# wbe.write_raster(wetland_upstream_raster, os.path.join(output_folder, "wetland_upstream.tif"))
# wbe.write_raster(wetland_extent_raster, os.path.join(output_folder, "wetland_extent.tif"))
# wbe.write_raster(wetland_outlet_raster, os.path.join(output_folder, "wetland_outlet.tif"))
# wbe.write_raster(wetland_modified_raster, os.path.join(output_folder, "wetland_modified.tif"))
# wbe.write_raster(flow_dir_raster, os.path.join(output_folder, "flow_dir_modified.tif"))

wetland_upstream_raster = wbe.read_raster(os.path.join(output_folder, "wetland_upstream.tif"))
wetland_outlet_raster = wbe.read_raster(os.path.join(output_folder, "wetland_outlet.tif"))
flow_dir_raster = wbe.read_raster(os.path.join(output_folder, "flow_dir_modified.tif"))
flow_tree, wetland_flowpath_raster = wetland.find_flow_path(wetland_raster, wetland_outlet_raster, flow_dir_raster,wetland_upstream_raster)
wbe.write_raster(wetland_flowpath_raster, os.path.join(output_folder, "wetland_flow_path.tif"))

# ********************** First,run Raise_watershed *************************
# The path of input files
# Watershed_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Watershed_raster.tif'
# Burn_DEM_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Burn_DEM.tif'

# Open data,get array,projection,geotranform,nodata
# Watershed_extent=Raster.get_raster(Watershed_file)
# Burn_DEM=Raster.get_raster(Burn_DEM_file)
# proj,geo,watershed_nodata=Raster.get_proj_geo_nodata(Watershed_file)
# _,_,DEM_nodata=Raster.get_proj_geo_nodata(Burn_DEM_file)

# run function,remember to change the path of the output results,which are located at the end of the function.
# Raise_watershed(Watershed_extent,Burn_DEM,proj,geo,watershed_nodata,DEM_nodata)

# ************************* Second,run IMWEBS_wetland **************************
# The path of input files
# wetland_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\wetland.tif'
# Dir_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\Dir.tif'
# Acc_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\run_data\ACC.tif'

# Open data,get array,projection,geotranform,nodata
# wetland=Raster.get_raster(wetland_file)
# Dir=Raster.get_raster(Dir_file)
# Acc=Raster.get_raster(Acc_file)
# proj,geo,wetland_nodata=Raster.get_proj_geo_nodata(wetland_file)

# Area_thre=45000  # 0.045 km2
# Acc_thre=0
# size=15  # size of cell
# run function,remember to change the path of the output results,which are located at the end of the function.
# IMWEBS_wetland(wetland,Dir,Acc,Area_thre,Acc_thre,proj,geo,wetland_nodata,size)

# ************************* Third,run build_wetland_flow_path *************************
# Note:The input files are all the second function's output results.
# Outlet_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\OUTLETS.tif'
# Dir_modified_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\Dir_modified.tif'   # It is the modified Dir,which is dfferent from the second Dir.
# wetland_modified_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\WETLAND.tif'   # It is the modified wetland,which is dfferent from the second wetland.
# LS_file=r'F:\IMWEBS\DATA\20240528_select_wts\15\RESULT\LS2.tif'

# Open data,get array,projection,geotranform,nodata
# Outlet=Raster.get_raster(Outlet_file)
# Dir_modified=Raster.get_raster(Dir_modified_file)
# wetland_modified=Raster.get_raster(wetland_modified_file)
# LS=Raster.get_raster(LS_file)
# proj,geo,wetland_nodata=Raster.get_proj_geo_nodata(wetland_modified_file)

# run function,remember to change the path of the output results,which are located at the end of the function.
# build_wetland_flow_path(Outlet,Dir_modified,wetland_modified,LS,wetland_nodata,proj,geo)

# Note: Above functions output the raster result(.tif). If users want to get shapefile,they need to make by tools of Arcgis/wbt.

