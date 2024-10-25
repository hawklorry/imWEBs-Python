from .bmp_reach import ReachBMP
from ..database.bmp.bmp_28_manure_catch_basin import ManureCatchBasinParameter

class ReachBMPManureCatchBasin(ReachBMP):
    def __init__(self, bmp_vector, subbasin_raster):
        super().__init__(bmp_vector, subbasin_raster)

        self.__manure_catch_basin_parameters = None

    @property
    def manure_catch_basin_parameters(self):
        if self.__manure_catch_basin_parameters is None:
            self.__manure_catch_basin_parameters = []

            for id, subbasin in self.subbasins.items():
                self.__manure_catch_basin_parameters.append(ManureCatchBasinParameter(id,subbasin,-1))

        return self.__manure_catch_basin_parameters