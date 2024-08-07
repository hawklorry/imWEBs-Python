from whitebox_workflows import Raster, WbEnvironment
import pandas as pd
from io import StringIO
from .raster_extension import RasterExtension

class Lookup():
    """
    lookup table for raster conversion
    """

    def __init__(self, lookup_csv_file:str, original_raster:Raster) -> None:
        self.csv_file = lookup_csv_file
        self.original_raster = original_raster
        
        #load lookup relationship from csv file assuming it has header and the original id and imwebs id is in first and second column
        df = pd.read_csv(self.csv_file, usecols=[0, 1], index_col=0)
        self.lookup_dict = df[df.columns[0]].to_dict()
        self.lookup_list = []

        #get unique values in original raster
        wbe = WbEnvironment()
        values = wbe.list_unique_values_raster(original_raster)
        df = pd.read_csv(StringIO(values), sep =",", usecols = [0], dtype = "int")
        self.raster_ids = df[df.columns[0]].to_list()

        #make sure the raster ids is included in the lookup table
        non_exist_ids = [id for id in self.raster_ids if id not in self.lookup_dict]
        if len(non_exist_ids) > 0:
            raise ValueError(f"Raster contains ids that are not in the lookup table: {non_exist_ids}.")
        
        #could also test that the imwebs ids are available in the soil/landuse parameter table
        
        #create the mapped raster using the lookup list
        self.mapped_raster = RasterExtension.reclassify(self.original_raster, self.lookup_dict)

if __name__ == '__main__':
    wbe = WbEnvironment()
    soil_raster = wbe.read_raster(r"C:\Work\imWEBs\test\test_model\watershed\input\soil.tif")
    lookup = Lookup(r"C:\Work\imWEBs\test\test_model\watershed\input\soilLookup.csv", soil_raster)
    wbe.write_raster(lookup.mapped_raster,r"C:\Work\imWEBs\test\test_model\watershed\input\soil_mapped.tif")
                                  
        
