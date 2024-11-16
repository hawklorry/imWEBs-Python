
#from imWEBs.database.reach_parameter import ReachParameter
# from imWEBs.outputs import outputs
# from imWEBs.database.bmp.reach import Reach
# from imWEBs.database.bmp.field_subbasin import FieldSubbasin
from whitebox_workflows import WbEnvironment
from imWEBs.vector_extension import VectorExtension
from imWEBs.delineation.structure import Structure
import os
import logging
import datetime
logger = logging.getLogger(__name__)

class cl:
    def __init__(self):
        self.col = 0

cl1 = cl()

wbe = WbEnvironment()
os.chdir(r"C:\Work\imWEBs\test\test_tutoriral_whitebox\backup")
logging.basicConfig(filename= f'imwebs_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log', 
                        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dem_raster = wbe.read_raster("dem_mdfy_streamBurned.tif")
structure_vector = wbe.read_vector("mergedBurn.shp")
outlet_vector = VectorExtension.add_id_for_raster_value(wbe.raster_to_vector_points(wbe.read_raster("combinedOutlets.tif")))

struc = Structure(structure_type= "combined",
                 output_folder= r"C:\Work\imWEBs\test\test_tutoriral_whitebox\backup\test",
                 dem_raster=dem_raster,
                 structure_polygon_vector=structure_vector,
                 structure_outlet_point_vector=outlet_vector)

flow_dir_raster = struc.generate_flow_direction_raster_shawn()
struc.save_raster(flow_dir_raster, "flow_dir_test.tif")


# brc_tiffs = r"C:\Work\imWEBs\Interface\BRC_TIFFs"
# parameter_database_file = r"C:\Work\imWEBs\BRC\model\Buffer_5m\database\parameter.db3"
# bmp_database_file = r"C:\Work\imWEBs\BRC\model\Buffer_5m\Buffer_5m\BMP.db3"
# my_outputs = outputs(brc_tiffs, brc_tiffs, parameter_database_file, bmp_database_file)
# reach = Reach(my_outputs)
# df = reach.build_reach_parameters()
# df.to_csv(r"C:\Work\imWEBs\Interface\BRC_TIFFs\test\reach_parameters.csv")

# parameter_db3 = r"C:\Work\imWEBs\BRC\model\Buffer_5m\database\parameter.db3"
# bmp_db3 = r"C:\Work\imWEBs\BRC\model\Buffer_5m\Buffer_5m\BMP.db3"
# parameters = parameters(parameter_db3, bmp_db3)

# attributes = [attr for attr in dir(ReachParameter) if not callable(getattr(ReachParameter, attr))]
# print(attributes)  # Output: ['a', 'b']

# p = ReachParameter()
# dict = p.to_dict()
# print(dict)

# print(ReachParameter.get_columns())

# reach_parameters = []
# for row in range(10):
#     reach_parameters.append(ReachParameter())
# df = pd.DataFrame([p.to_dict() for p in reach_parameters])
# print(df)

