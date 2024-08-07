from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from ..database_base import DatabaseBase
from .landuse_lookup import LanduseLookup
from .soil_lookup import SoilLookup


class ParameterDatabase(DatabaseBase):
    """Access to parameter database."""

    def __init__(self, database_file):
        super().__init__(database_file)     
        self._lookup_tables = {}
        self.__load()

    def __load(self):    
        self.soil_lookup = {}
        self.landuse_lookup = {}
        self.algricultural_landuses = []

        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            select_stmt = select(SoilLookup)
            for row in session.scalars(select_stmt):
                self.soil_lookup[row.SOILCODE] = row

            select_stmt = select(LanduseLookup)
            for row in session.scalars(select_stmt):
                self.landuse_lookup[row.LANDUSE_ID] = row
                if row.is_agricultrual:
                    self.algricultural_landuses.append(row.LANDUSE_ID)

    def get_parameter_lookup(self, parameter_name, parameter_type):
        """return lookup array to be used in reclass funciton"""
        if parameter_name in self._lookup_tables:
            return self._lookup_tables[parameter_name]
        
        lookups = []
        if parameter_type == "soil":
            values = self.soil_lookup.items()
        elif parameter_type == "landuse":
            values = self.landuse_lookup.items()
        for key, value in values:
            lookups.append([key, getattr(value, parameter_name)])
        
        self._lookup_tables[parameter_name] = lookups

        return lookups

    def get_potential_runoff_coefficient(self, landuse, soil)->float:
        return self.landuse_lookup[landuse].getPotentialRunoffCoefficient(self.soil_lookup[soil].TEXTURE)

    def get_depression_storage_capacity(self, landuse, soil)->float:
        return self.landuse_lookup[landuse].getDepressionStorageCapacity(self.soil_lookup[soil].TEXTURE)

    def get_slope(self, landuse, soil)->float:
        return self.landuse_lookup[landuse].getSlope(self.soil_lookup[soil].TEXTURE)

    def get_cn2(self, landuse, soil)->float:
        return self.landuse_lookup[landuse].getCN2(self.soil_lookup[soil].HG)

    def get_impervious_ratio(self, landuse)->float:
        return self.landuse_lookup[landuse].FIMP