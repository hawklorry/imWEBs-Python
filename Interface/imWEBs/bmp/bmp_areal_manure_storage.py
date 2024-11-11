from .bmp_areal import ArealBMP
from ..vector_extension import VectorExtension
from ..database.bmp.bmp_27_manure_storage import ManureStorageParameter, ManureStorageManagement
from ..names import Names

class ArealBMPManureStorage(ArealBMP):
    """Manure Storage"""
    def __init__(self, bmp_vector, flow_direction_raster, subbasin_raster, reach_raster, dem_raster):
        super().__init__(bmp_vector, flow_direction_raster, subbasin_raster, reach_raster, dem_raster)
        
        self.__manure_storage_parameters = None

    @property
    def manure_storage_parameters(self)->list:
        if self.__manure_storage_parameters is None: 
            self.__manure_storage_parameters = []
            feedlots = VectorExtension.get_unique_field_value(self.bmp_vector, Names.field_name_feedlot)            
            for id, subbasin in self.subbasins:
                contribution_area_ha = self.contribution_area_ha[id]
                drainage_fraction = self.contribution_area_subbasin_ratio[id]
                distance_to_reach = self.reach_distance[id]
                height_to_reach = self.reach_elevation_drop[id]

                self.__manure_storage_parameters.append(
                    ManureStorageParameter(id, 
                                           subbasin, 
                                           0 if id not in feedlots else feedlots[id], #feedlot id
                                           contribution_area_ha, 
                                           drainage_fraction, 
                                           distance_to_reach, 
                                           height_to_reach))

        return self.__manure_storage_parameters