from .bmp_areal import ArealBMP
from ..vector_extension import VectorExtension
from ..database.bmp.bmp_29_manure_feedlot import ManureFeedlot, ManureFeedlotManagement
from ..names import Names
import pandas as pd

class ArealBMPManureFeedlot(ArealBMP):
    """Manure Storage"""
    def __init__(self, bmp_vector, flow_direction_raster, subbasin_raster, reach_raster, dem_raster):
        super().__init__(bmp_vector, flow_direction_raster, subbasin_raster, reach_raster, dem_raster)
        
        self.__manure_feedlot_parameters = None
        self.__manure_feedlot_managements = None

    @property
    def parameters(self)->list:
        if self.__manure_feedlot_parameters is None: 
            self.__manure_feedlot_parameters = []

            feedlot_animal_ids = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_animal_id)  
            feedlot_catchbasin_ids = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_catch_basin)  
            for id, subbasin in self.subbasins.items():
                self.__manure_feedlot_parameters.append(
                    ManureFeedlot(  id, 
                                    feedlot_animal_ids[id], #animal id must be sepcified
                                    subbasin, 
                                    0 if id not in feedlot_catchbasin_ids else feedlot_catchbasin_ids[id]))

        return self.__manure_feedlot_parameters
    
    @property
    def default_management_df(self)->pd.DataFrame:
        """Default managements populated with the feedlot attributes"""
        if self.__manure_feedlot_managements is None:
            feedlot_adults = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_adult)
            feedlot_non_adults = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_non_adult)
            feedlot_storage_ids = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_storage_ids, str)
            feedlot_storage_ratios = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot_storage_ratios, str)
            managements = [ManureFeedlotManagement(id, 
                                                   0 if id not in feedlot_adults else feedlot_adults[id],
                                                   0 if id not in feedlot_non_adults else feedlot_non_adults[id],
                                                   "" if id not in feedlot_storage_ids else feedlot_storage_ids[id],
                                                   "" if id not in feedlot_storage_ratios else feedlot_storage_ratios[id],
                                                   ) for id in self.ids]
            
            self.__manure_feedlot_managements = pd.DataFrame([vars(rb) for rb in managements])

        return self.__manure_feedlot_managements


              
       
