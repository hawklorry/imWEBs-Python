from .bmp_reach import ReachBMP
from ..database.bmp.bmp_03_reservoir import Reservoir

class ReachBMPReservoir(ReachBMP):
    def __init__(self, bmp_vector, subbasin_raster):
        super().__init__(bmp_vector, subbasin_raster)

        self.__reservoirs = None

    @property
    def reservoirs(self):
        if self.__reservoirs is None:
            self.__reservoirs = []

            for id in self.subbasins.keys():
                self.__reservoirs.append(Reservoir(id))

        return self.__reservoirs