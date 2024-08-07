
#from imWEBs.database.reach_parameter import ReachParameter
from imWEBs.Interface.imWEBs.outputs import outputs
from imWEBs.database.bmp.reach import Reach
from imWEBs.database.bmp.field_subbasin import FieldSubbasin

#fs = FieldSubbasin()
#print(fs)

brc_tiffs = r"C:\Work\imWEBs\Interface\BRC_TIFFs"
parameter_database_file = r"C:\Work\imWEBs\BRC\model\Buffer_5m\database\parameter.db3"
bmp_database_file = r"C:\Work\imWEBs\BRC\model\Buffer_5m\Buffer_5m\BMP.db3"
my_outputs = outputs(brc_tiffs, brc_tiffs, parameter_database_file, bmp_database_file)
reach = Reach(my_outputs)
df = reach.build_reach_parameters()
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

