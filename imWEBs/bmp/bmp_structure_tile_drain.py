from .bmp import BMP
from whitebox_workflows import Vector, Raster
import pandas as pd
from ..delineation.structure import Structure
from ..database.bmp.bmp_19_tile_drain_management import TileDrainParameter
from ..vector_extension import VectorExtension
from ..raster_extension import RasterExtension
import numpy as np

class StructureBMPTileDrain(BMP):
    field_name_tile_drain_depth = "depth"
    field_name_tile_drain_spacing = "spacing"

    fields_tile_drain = [
        field_name_tile_drain_depth,
        field_name_tile_drain_spacing
    ]

    def __init__(self, bmp_vector:Vector, bmp_raster:Vector, subbasin_raster:Raster, field_raster:Raster, dem_raster:Raster):
        super().__init__(bmp_vector, subbasin_raster)

        self.field_raster = field_raster
        self.dem_raster = dem_raster
        self.bmp_raster_original = bmp_raster

    @property
    def tile_drain_df(self)->pd.DataFrame:
        dict_depth = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_depth, float)
        dict_spacing = VectorExtension.get_unique_field_value(self.bmp_vector, StructureBMPTileDrain.field_name_tile_drain_spacing, float)
        dict_field = VectorExtension.get_unique_field_value(self.bmp_vector, "FieldId", int)
        dict_subbasin = VectorExtension.get_unique_field_value(self.bmp_vector, "SubbasinId", int)

        dict_elevation = RasterExtension.get_zonal_statistics(self.dem_raster, self.bmp_raster_original,"mean","elevation")["elevation"].to_dict()        
        dict_area_ha = RasterExtension.get_category_area_ha_dataframe(self.bmp_raster_original,"area_ha")["area_ha"].to_dict()

        tile_drains = []
        #some tile drain field may not be included.
        for id, depth in dict_depth.items():
            tile_drains.append(TileDrainParameter(
                id,
                dict_field[id],
                dict_subbasin[id],
                depth,
                dict_spacing[id],
                dict_elevation[id],
                dict_area_ha[id] * 100  #m^3
            ))

        return pd.DataFrame([vars(rb) for rb in tile_drains])

    @staticmethod
    def validate(tile_drain_boundary_vector:Vector):
        """
        check tile drain boundary layer
        """
        if tile_drain_boundary_vector is None:
            return
        
        #make sure tile drain has all required columns
        VectorExtension.check_fields_in_vector(tile_drain_boundary_vector, StructureBMPTileDrain.fields_tile_drain)