from whitebox_workflows import WbEnvironment, Vector
from io import StringIO
import pandas as pd
import geopandas as gpd

class VectorExtension:

    @staticmethod
    def compare_vector_projection(vector1:Vector, vector2:Vector):
        """Check if the raster have same size as the standard raster """
        return vector1.projection == vector2.projection
        
    
    @staticmethod
    def compare_vectors(vectors):
        if len(vectors) <= 1:
            return True
        
        is_same = True
        standard_vector = None
        for key, value in vectors.items():
            if standard_vector is None:
                standard_vector = value
                continue

            if not VectorExtension.compare_vector_projection(standard_vector, value):
                is_same = False
                print(f"The extend of {value.file_name} doesn't match {standard_vector.file_name}")

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

