from imWEBs.database.bmp.bmp_database import BMPDatabase
from imWEBs.database.bmp.farm_info import FarmInfo
from imWEBs.Interface.imWEBs.outputs import outputs

farm_info = FarmInfo(10,10)
print(BMPDatabase.COL_NAME_AREA_HA)


brc_tiffs = r"C:\Work\imWEBs\Interface\BRC_TIFFs"
parameter_database_file = r"C:\Work\imWEBs\test\parameter.db3"
bmp_database_file = r"C:\Work\imWEBs\test\BMP_Test.db3"
my_outputs = outputs(brc_tiffs, brc_tiffs, parameter_database_file, bmp_database_file)

my_outputs.generate_bmp_database()



