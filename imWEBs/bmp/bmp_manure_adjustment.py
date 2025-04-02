from whitebox_workflows import Raster
from ..database.bmp.bmp_21_manure_incorporation_within_48h import ManureIncorporationWithin48hManagement
from ..database.bmp.bmp_22_manure_application_setback import ManureApplicationSetbackManagement
from ..database.bmp.bmp_23_no_application_on_snow import ManureNoApplicaitonOnSnowManagement
from ..database.bmp.bmp_24_spring_application_rather_than_fall_application import ManureSpringApplicationRatherThanFallApplicationManagement
from ..database.bmp.bmp_25_application_based_on_soil_nitrogen_limit import ManureApplicationBasedOnSoliNitrogenLimitManagement
from ..database.bmp.bmp_26_application_based_on_soil_phosphorous_limit import ManureApplicationBasedOnPhosphorousLimitManagement
from enum import Enum
import pandas as pd
from ..raster_extension import RasterExtension
from ..names import Names

class ManureAdjustmentBMPType(Enum):
    INCORPORATION_WITHIN_48H = 21
    APPLICATION_SETBACK = 22
    NO_APPLICATION_ON_SNOW = 23
    SPRING_APPLICATION = 24
    APPLICATION_ON_N_LIMIT = 25
    APPLICATION_ON_P_LIMIT = 26


class ManureAdjustmentBMP:
    def __init__(self, bmp_raster:Raster, adjustment_type:ManureAdjustmentBMPType):
        self.bmp_raster = bmp_raster
        self.adjustment_type = adjustment_type

    @property
    def table_name(self):
        if self.adjustment_type == ManureAdjustmentBMPType.INCORPORATION_WITHIN_48H:
            return Names.bmp_table_name_manure_incorporation_within_48h_management
        elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_SETBACK:
            return Names.bmp_table_name_manure_application_setback_management
        elif self.adjustment_type == ManureAdjustmentBMPType.NO_APPLICATION_ON_SNOW:
            return Names.bmp_table_name_manure_no_application_on_snow_management
        elif self.adjustment_type == ManureAdjustmentBMPType.SPRING_APPLICATION:
            return Names.bmp_table_name_manure_spring_application_rather_than_fall_application_management
        elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_ON_N_LIMIT:
            return Names.bmp_table_name_manure_application_based_on_soil_nitrogen_limit_management
        elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_ON_P_LIMIT:
            return Names.bmp_table_name_manure_application_based_on_soil_phosphorous_limit_management

    @property
    def manure_adjustment_df(self):
        locations = RasterExtension.get_unique_values(self.bmp_raster)

        bmps = []
        for loc in locations:
            if self.adjustment_type == ManureAdjustmentBMPType.INCORPORATION_WITHIN_48H:
                bmps.append(ManureIncorporationWithin48hManagement(loc))
            elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_SETBACK:
                bmps.append(ManureApplicationSetbackManagement(loc))
            elif self.adjustment_type == ManureAdjustmentBMPType.NO_APPLICATION_ON_SNOW:
                bmps.append(ManureNoApplicaitonOnSnowManagement(loc))
            elif self.adjustment_type == ManureAdjustmentBMPType.SPRING_APPLICATION:
                bmps.append(ManureSpringApplicationRatherThanFallApplicationManagement(loc))
            elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_ON_N_LIMIT:
                bmps.append(ManureApplicationBasedOnSoliNitrogenLimitManagement(loc))
            elif self.adjustment_type == ManureAdjustmentBMPType.APPLICATION_ON_P_LIMIT:
                bmps.append(ManureApplicationBasedOnPhosphorousLimitManagement(loc))

        return pd.DataFrame([vars(rb) for rb in bmps])
