from .bmp import BMP
from whitebox_workflows import Vector, Raster
import pandas as pd
from ..delineation.structure import Structure
from ..database.bmp.bmp_41_wascob import Wascob
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
import numpy as np

class StructureBMPWascob(BMP):
    field_name_wascob_year = "year"
    field_name_wascob_outlet = "outlet"
    field_name_wascob_height = "height"
    field_name_wascob_max_volume = "max_vol"
    field_name_wascob_max_area = "max_area"
    field_name_wascob_drainage_capacity = "capacity"

    fields_wascob = [
        field_name_wascob_year,
        field_name_wascob_outlet,
        field_name_wascob_height,
        field_name_wascob_max_volume,
        field_name_wascob_max_area,
        field_name_wascob_drainage_capacity
    ]

    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster, structure:Structure, field_raster:Raster, dem_raster:Raster, wascob_outlet_vector:Vector):
        super().__init__(bmp_vector, subbasin_raster)

        self.structure = structure
        self.field_raster = field_raster
        self.dem_raster = dem_raster
        self.wascob_outlet_vector = wascob_outlet_vector

    @property
    def wascob_df(self)->pd.DataFrame:
        dict_year = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_year, int)
        dict_outlet_id = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_outlet, int)
        dict_height = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_height, float)
        dict_max_volume = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_max_volume, float)
        dict_max_area = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_max_area, float)
        dict_capacity = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPWascob.field_name_wascob_drainage_capacity, float)

        dict_elevation = RasterExtension.get_zonal_statistics(self.dem_raster, self.structure.boundary_raster,"mean","elevation")["elevation"].to_dict()
        dict_field = RasterExtension.get_zonal_statistics(self.field_raster, self.structure.boundary_raster,"max","field")["field"].to_dict()

        wascob_outlet_raster = VectorExtension.vector_to_raster(self.wascob_outlet_vector, self.structure.boundary_raster)
        dict_outlet_subbasin = RasterExtension.get_zonal_statistics(self.subbasin_raster, wascob_outlet_raster,"max","subbasin")["subbasin"].to_dict()

        dict_subbasin = RasterExtension.get_zonal_statistics(self.subbasin_raster, self.structure.boundary_raster,"max","subbasin")["subbasin"].to_dict()

        wascobs = []
        for id, att in self.structure.attributes.items():
            wascobs.append(Wascob(id, att.contribution_area, 
                                  1900 if id not in dict_year else dict_year[id], 
                                  dict_field[id], 
                                  dict_subbasin[id],
                                  dict_outlet_subbasin[dict_outlet_id[id]], 
                                  dict_elevation[id] + (2 if id not in dict_height else dict_height[id]),
                                  0.02 if id not in dict_max_volume else dict_max_volume[id],
                                  0.1 if id not in dict_max_area else dict_max_area[id],
                                  dict_capacity[id]))

        return pd.DataFrame([vars(rb) for rb in wascobs])

    @staticmethod
    def validate(wascob_boundary_vector:Vector,
                 wascob_outlet_vector:Vector):
        """
        check wascob boundary and outlet layer

        1. wascob outlet layer must be provied for wascob. 
        2. The outlet id in wascob boundary layer must exist in outlet layer.
        """
        if wascob_boundary_vector is None:
            return

        if wascob_boundary_vector is not None and wascob_outlet_vector is None:
            raise ValueError("Wascob outlets shapefile is not provided.")
        
        #make sure wascob has all required columns
        VectorExtension.check_fields_in_vector(wascob_boundary_vector, StructureBMPWascob.fields_wascob)  

        #check wascob outlet id
        wascob_outlet_ids = VectorExtension.get_unique_ids(wascob_outlet_vector)
        wascob_outlet_ids_in_boundary = VectorExtension.get_unique_field_value(wascob_boundary_vector, StructureBMPWascob.field_name_wascob_outlet)

        if not np.array_equal(wascob_outlet_ids.sort(), list(wascob_outlet_ids_in_boundary.values()).sort()):
            raise ValueError("Wascob outlet id doesn't existin in wascob outlet layer or not all wascob outlets are assigned to a wascob. ")

