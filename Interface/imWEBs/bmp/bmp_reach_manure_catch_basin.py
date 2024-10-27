from .bmp_reach import ReachBMP
from ..database.bmp.bmp_28_manure_catch_basin import ManureCatchBasinParameter
from whitebox_workflows import Vector, Raster
import pandas as pd

class ReachBMPManureCatchBasin(ReachBMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster, reach_parameter_df:pd.DataFrame):
        super().__init__(bmp_vector, subbasin_raster)

        self.reach_parameter_df = reach_parameter_df
        self.__manure_catch_basin_parameters = None
        

    @property
    def manure_catch_basin_parameters(self):
        if self.__manure_catch_basin_parameters is None:
            self.__manure_catch_basin_parameters = []

            reach_id_receive_reach_id_dict = {}
            if self.reach_parameter_df is not None:
                reach_id_receive_reach_id_dict = self.reach_parameter_df.set_index("reach_id")["receive_reach_id"].to_dict()
            for id, subbasin in self.subbasins.items():
                receive_reach_id = -1
                if subbasin in reach_id_receive_reach_id_dict:
                    receive_reach_id = reach_id_receive_reach_id_dict[subbasin]
                self.__manure_catch_basin_parameters.append(ManureCatchBasinParameter(id,subbasin,receive_reach_id))

        return self.__manure_catch_basin_parameters