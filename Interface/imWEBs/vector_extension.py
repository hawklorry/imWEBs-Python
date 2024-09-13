from whitebox_workflows import WbEnvironment, Vector
from io import StringIO
import pandas as pd
import geopandas as gpd
import logging
logger = logging.getLogger(__name__)

class VectorExtension:

    ID_FIELD_NAME = "id"

    @staticmethod
    def check_unique_id(vector:Vector)->bool:
        """check if the the vector has the ID column and values are unique"""
        field_names = [field.name.lower() for field in vector.get_attribute_fields()]
        if VectorExtension.ID_FIELD_NAME not in field_names:
            return False
        
        field_index = field_names.index(VectorExtension.ID_FIELD_NAME)
        field_name = vector.get_attribute_fields()[field_index].name
        ids = []
        for i in range(vector.num_records):
            id = int(vector.get_attribute_value(i, field_name).get_value_as_f64())
            if id in ids:
                return False
            ids.append(id)

        return True

    @staticmethod
    def compare_vector_projection(vector1:Vector, vector2:Vector):
        """Check if the raster have same size as the standard raster """
        return vector1.projection == vector2.projection
        
    
    @staticmethod
    def check_vectors(vectors:dict)->bool:
        """Compare all vectors in the dictionary and return true when all of them has the same projection."""
        if len(vectors) <= 1:
            return True
        
        is_same = True
        standard_vector = None
        for key, value in vectors.items():
            logger.debug(f"Checking ID column in {{value.file_name}} ...")
            if not VectorExtension.check_unique_id(value):
                raise ValueError(f"ID column was not found in {value.file_name}.")

            if standard_vector is None:
                standard_vector = value
                continue

            if not VectorExtension.compare_vector_projection(standard_vector, value):
                is_same = False
                raise ValueError(f"The extend of {value.file_name} doesn't match {standard_vector.file_name}")

        return is_same
    
    @staticmethod
    def save_vector(vector:Vector, destination_file:str):
        #wbe = WbEnvironment()
        #wbe.write_vector(vector, destination_file)

        gpd.read_file(vector.file_name).to_file(destination_file)

    @staticmethod
    def check_field_in_vector(vector:Vector, field_name:str):
        """
        check if vector has attribute with given name
        """
        return len([field for field in vector.get_attribute_fields() if field.name == field_name]) > 0

