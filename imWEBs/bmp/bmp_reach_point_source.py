from .bmp_reach import ReachBMP
from ..database.bmp.bmp_01_point_source import PointSource
from ..database.hydroclimate.hydroclimate_database import HydroClimateDatabase
from whitebox_workflows import Vector, Raster
from ..vector_extension import VectorExtension
import logging
logger = logging.getLogger(__name__)

class ReachBMPPointSource(ReachBMP):
    
    field_name_reservoir_operation = "Operation"
    field_name_reservoir_table_name = "TableName"

    fields_point_source = [
        field_name_reservoir_operation,
        field_name_reservoir_table_name
    ]

    

    def __init__(self, point_source_vector:Vector, 
                subbasin_raster:Raster):
        super().__init__(point_source_vector, subbasin_raster)       
        self.__point_sources = None

    @staticmethod
    def validate(point_source_vector:Vector, hydro_climate_database:HydroClimateDatabase = None):
        if point_source_vector is None:
            return
        
        #make sure the shapefile has required columns
        VectorExtension.check_fields_in_vector(point_source_vector, ReachBMPPointSource.fields_point_source)

        #make sure all point source has a table name
        dict_table_names = VectorExtension.get_unique_field_value(point_source_vector, ReachBMPPointSource.field_name_reservoir_table_name,str)
        point_source_ids = VectorExtension.get_unique_ids(point_source_vector)

        if len(point_source_ids) > len(dict_table_names):
            raise ValueError(f"Following point sources {[x for x in point_source_ids if x not in dict_table_names]} doesn't have table names.")

        #check the table name exist in hydroclimate database and the data is in required format
        if hydro_climate_database is not None:            
            for id, table_name in dict_table_names.items():
                hydro_climate_database.validate_measured_data_table(table_name)
        else:
            logger.info("Hydroclimate database is not specified so the table names are not valiated.")
        
    @property
    def point_sources(self):
        if self.__point_sources is None:
            self.__point_sources = []

            dict_operations = VectorExtension.get_unique_field_value(self.bmp_vector, ReachBMPPointSource.field_name_reservoir_operation,str)
            dict_table_names = VectorExtension.get_unique_field_value(self.bmp_vector, ReachBMPPointSource.field_name_reservoir_table_name,str)

            for id, table_name in dict_table_names.items():
                ps = PointSource(id)
                ps.TABLENAME = table_name

                if id in dict_operations:
                    ps.OPERATION = dict_operations[id]

                self.__point_sources.append(ps)

        return self.__point_sources