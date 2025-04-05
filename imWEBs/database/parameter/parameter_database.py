from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from ..database_base import DatabaseBase
from .landuse_lookup import LanduseLookup
from .soil_lookup import SoilLookup
import logging
logger = logging.getLogger(__name__)

class ParameterDatabase(DatabaseBase):
    """Access to parameter database."""

    default_tables = ["Climate", 
                      "Discharge", 
                      "Interception",
                      "NutrientCycling",
                      "PlantGrowth",
                      "Sediment",
                      "Snow",
                      "SubArea",
                      "WaterBalance",
                      "Wetland",
                      "LanduseLookup",
                      "SoilLookup", 
                      "LanduseSoilLoopUpCalibration",
                      "Lapse_rate", 
                      "LS_parameter",
                      "tile_drain"]

    def __init__(self, database_file):
        super().__init__(database_file) 

        self._lookup_tables = {}
        self._soil_lookup = {}
        self._landuse_lookup = {}
        self._non_agricultural_landuses = []
        self._tame_grass_landuses = []

    def __populate_default_tables(self):
        """populate default parameter tables from csv files"""

        #populate default tables
        logger.info("Trying to load default tables to parameter database ...")
        for table in ParameterDatabase.default_tables:
            logger.info(table)
            self.populate_defaults(table)

#region Soil and Landuse Parameters


    @property
    def soil_lookup(self)->dict:
        if len(self._soil_lookup) == 0:
            self.__populate_default_tables()

            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                select_stmt = select(SoilLookup)
                for row in session.scalars(select_stmt):
                    self._soil_lookup[row.SOILCODE] = row

        return self._soil_lookup
    
    @property
    def landuse_lookup(self)->dict:
        if len(self._landuse_lookup) == 0:
            self.__populate_default_tables()

            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                select_stmt = select(LanduseLookup)
                for row in session.scalars(select_stmt):
                    self._landuse_lookup[row.LANDUSE_ID] = row
                    if not row.is_agricultrual:
                        self._non_agricultural_landuses.append(row.LANDUSE_ID)
                    if row.is_tame_grass:
                        self._tame_grass_landuses.append(row.LANDUSE_ID)

        return self._landuse_lookup

    @property
    def non_agricultural_landuse_ids(self)->dict:
        landuse = self.landuse_lookup
        return self._non_agricultural_landuses
    
    @property
    def tame_grass_landuse_ids(self)->dict:
        landuse = self.landuse_lookup
        return self._tame_grass_landuses

    def get_parameter_lookup(self, parameter_name, parameter_type):
        """return lookup array to be used in reclass funciton"""

        if parameter_name in self._lookup_tables:
            return self._lookup_tables[parameter_name]
        
        lookups = []
        if parameter_type == "soil":
            values = self.soil_lookup.items()
        elif parameter_type == "landuse":
            values = self.landuse_lookup.items()
        else:
            raise ValueError(f"Invalide parameter type {parameter_type}. Please use either soil or landuse.")
        for key, value in values:
            lookups.append([key, getattr(value, parameter_name)])
        
        self._lookup_tables[parameter_name] = lookups

        return lookups

    def get_soil_texture(self, soil:str)->int:
        if soil not in self.soil_lookup:
            raise ValueError(f"Soil {soil} doesn't exist in parameter soil lookup table.")
        return int(self.soil_lookup[soil].TEXTURE)

    def get_potential_runoff_coefficient(self, landuse, soil:str)->float:
        """Get potential runoff coefficient for given landuse and soil"""
        return self.landuse_lookup[landuse].getPotentialRunoffCoefficient(self.get_soil_texture(soil))

    def get_depression_storage_capacity(self, landuse, soil)->float:
        """Get depression storage capacity for given landuse and soil"""
        return self.landuse_lookup[landuse].getDepressionStorageCapacity(self.get_soil_texture(soil))

    def get_slope(self, landuse, soil)->float:
        """Get slope for given landuse and soil"""
        return self.landuse_lookup[landuse].getSlope(self.get_soil_texture(soil))

    def get_cn2(self, landuse, soil)->float:
        """Get CN2 for given landuse and soil"""
        return self.landuse_lookup[landuse].getCN2(self.soil_lookup[soil].HG)

    def get_impervious_ratio(self, landuse)->float:        
        """Get impervious ration for given landuse"""
        return self.landuse_lookup[landuse].FIMP
    
#endregion

    
#region Single Parameter

    def __get_single_parameter(self, parameter_table_name:str, parameter_name:str)->float:
        """get parameter value with given name and table"""
        return float(self.read_single_value(parameter_table_name, "Parameter", parameter_name, "Value"))

    @property
    def wetland_co1(self)->float:
        return self.__get_single_parameter("Wetland","Wet_Co1")
    
    @property
    def wetland_ex1(self)->float:
        return self.__get_single_parameter("Wetland","Wet_Ex1")   
    
    @property
    def wetland_co2(self)->float:
        return self.__get_single_parameter("Wetland","Wet_Co2")
    
    @property
    def wetland_cons(self)->float:
        return self.__get_single_parameter("Wetland","Wet_Cons")      
     
#endregion

#region IUH Parameter

    @property
    def iuh_max_min_v(self)->tuple[float,float]:
        return (self.__get_single_parameter("Discharge",f"maxV"),self.__get_single_parameter("Discharge",f"minV"))

    @property
    def iuh_2yr(self)->tuple[float,float]:
        return self.__get_iuh_radius_parameter(2)
    
    @property
    def iuh_10yr(self)->tuple[float,float]:
        return self.__get_iuh_radius_parameter(10)

    @property
    def iuh_100yr(self)->tuple[float,float]:
        return self.__get_iuh_radius_parameter(100)    
    
    def __get_iuh_radius_parameter(self, design_storm)->tuple[float,float]:
        return (self.__get_single_parameter("Discharge",f"radiusA{design_storm}"),self.__get_single_parameter("Discharge",f"radiusB{design_storm}"))


#endregion