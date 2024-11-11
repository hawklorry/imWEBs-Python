from .bmp_reach import ReachBMP
from ..database.bmp.bmp_03_reservoir import Reservoir
from ..vector_extension import VectorExtension
from ..names import Names
from whitebox_workflows import FieldData, Vector, Raster
import os
import pandas as pd

class ReachBMPReservoir(ReachBMP):
    FLOW_ROUTING_NAME_RATING_CURVE = "RAT_RES"
    FLOW_ROUTING_NAME_DAILY_OUTFLOW = "MDO_RES"
    FLOW_ROUTING_NAME_MONTHLY_OUTFLOW = "MMO_RES"
    FLOW_ROUTING_NAME_ANUNAL_RELEASE_RATE = "AAR_RES"
    FLOW_ROUTING_NAME_TARGET_RELEASE_RATE = "TRR_RES"

    SEDIMENT_ROUTING_NAME_MASS_BALANCE = "SMB_RES"
    NUTRIENT_ROUTING_NAME_MASS_BALANCE = "RES_NUTR_BAL"

    FLOW_ROUTING_METHODS = [
            FLOW_ROUTING_NAME_RATING_CURVE,
            FLOW_ROUTING_NAME_DAILY_OUTFLOW,
            FLOW_ROUTING_NAME_MONTHLY_OUTFLOW,
            FLOW_ROUTING_NAME_ANUNAL_RELEASE_RATE,
            FLOW_ROUTING_NAME_TARGET_RELEASE_RATE
    ]

    FLOW_ROUTING_METHODS_REQUIRING_EXTERNAL_DATA = [
            FLOW_ROUTING_NAME_RATING_CURVE,
            FLOW_ROUTING_NAME_DAILY_OUTFLOW,
            FLOW_ROUTING_NAME_MONTHLY_OUTFLOW
    ]

    RATING_CURVE_COLUMNS = [
        "storage","area","discharge"
    ]

    field_name_reservoir_operation = "op"
    field_name_reservoir_emergency_surface_area = "sa_em"
    field_name_reservoir_emergency_volume = "v_em"
    field_name_reservoir_principal_surface_area = "sa_pr"
    field_name_reservoir_principal_volume = "v_pr"
    field_name_reservoir_flow_data = "file"

    fields_reservoir = [
        field_name_reservoir_operation,
        field_name_reservoir_emergency_surface_area,
        field_name_reservoir_emergency_volume,
        field_name_reservoir_principal_surface_area,
        field_name_reservoir_principal_volume,
        field_name_reservoir_flow_data
    ]

    def __init__(self, reservoir_vector:Vector, 
                 subbasin_raster:Raster):
        super().__init__(reservoir_vector, subbasin_raster)       
        self.__reservoirs = None

    @staticmethod
    def validate(reservoir_vector:Vector,
                 flow_method:str = None, 
                 flow_data_folder:str = None):

        #make sure the shapefile has required columns
        VectorExtension.check_fields_in_vector(reservoir_vector, ReachBMPReservoir.fields_reservoir)

        if flow_method is None: 
            return

        #check the flow method and the corresponding file
        if flow_method not in ReachBMPReservoir.FLOW_ROUTING_METHODS:
            raise ValueError(f"User-define reservoir flow routing method - {flow_method} is not valid. The valid methods are: {', '.join(ReachBMPReservoir.FLOW_ROUTING_METHODS)}")
        
        if flow_method in ReachBMPReservoir.FLOW_ROUTING_METHODS_REQUIRING_EXTERNAL_DATA:
            if flow_data_folder is None or not os.path.exists(flow_data_folder):
                raise ValueError(f"Reservoir flow routing method {flow_method} requires external files. Couldn't find data folder {flow_data_folder}.")
            
            #all the external files should be in the flow_data_folder with an extension of csv and has the same name as specified in FILE columns
            _,field_name_id = VectorExtension.check_id(reservoir_vector) 
            for i in range(reservoir_vector.num_records):
                id = int(reservoir_vector.get_attribute_value(i, field_name_id).get_value_as_f64())
                file = reservoir_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_flow_data)
                if file.is_null() or len(file.get_as_string()) <= 0:
                    raise ValueError(f"FILE column is empty for reservoir {id}.")

                external_file = os.path.join(flow_data_folder, f"{file.get_as_string()}.csv")
                if not os.path.exists(external_file):
                    raise ValueError(f"Couldn't find {external_file} for reservoir {id}.")
                
                #check column in the csv file
                if flow_method == ReachBMPReservoir.FLOW_ROUTING_NAME_RATING_CURVE:
                    df = pd.read_csv(external_file)
                    for col in ReachBMPReservoir.RATING_CURVE_COLUMNS:
                        if col not in df.columns:
                            raise ValueError(f"Couldn't find column {col} in {external_file}. It should have three columns: {', '.join(ReachBMPReservoir.RATING_CURVE_COLUMNS)}")

    @property
    def reservoirs(self):
        if self.__reservoirs is None:
            self.__reservoirs = []
           
            _,field_name_id = VectorExtension.check_id(self.bmp_vector)            
            for i in range(self.bmp_vector.num_records):
                id = int(self.bmp_vector.get_attribute_value(i, field_name_id).get_value_as_f64())
                operation = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_operation)
                emergency_surface_area = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_emergency_surface_area)
                emergency_volume = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_emergency_volume)
                principal_surface_area = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_principal_surface_area)
                principal_volume = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_principal_volume)
                file = self.bmp_vector.get_attribute_value(i, ReachBMPReservoir.field_name_reservoir_flow_data)

                reservoir = Reservoir(id)
                if not operation.is_null():
                    reservoir.OPERATION = operation.get_as_string()
                if not emergency_surface_area.is_null():
                    reservoir.SA_EM = emergency_surface_area.get_value_as_f64()
                if not emergency_volume.is_null():
                    reservoir.V_EM = emergency_volume.get_value_as_f64()        
                if not principal_surface_area.is_null():
                    reservoir.SA_PR = principal_surface_area.get_value_as_f64()
                if not principal_volume.is_null():
                    reservoir.V_PR = principal_volume.get_value_as_f64() 
                if not file.is_null():
                    reservoir.FILE = file.get_as_string()      

                self.__reservoirs.append(reservoir)

        return self.__reservoirs