from whitebox_workflows import WbEnvironment, Vector, AttributeField, FieldDataType, FieldData, Raster
from io import StringIO
import pandas as pd
import geopandas as gpd
import logging
logger = logging.getLogger(__name__)

class VectorExtension:

    ID_FIELD_NAME = "id"

    @staticmethod
    def add_id_for_raster_value(vector:Vector)->Vector:
        if len([field.name for field in vector.get_attribute_fields() if field.name == "VALUE"]) <= 0:
            return vector

        id_field = AttributeField(VectorExtension.ID_FIELD_NAME, FieldDataType.Int, 6, 0)
        vector.add_attribute_field(id_field)

        for i in range(vector.num_records):
            value = vector.get_attribute_value(i, "VALUE").get_value_as_f64()
            vector.set_attribute_value(i,VectorExtension.ID_FIELD_NAME,FieldData.new_int(int(value)))
        return vector


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

        return True, field_name, ids

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
            logger.info(f"Checking ID column in {value.file_name} ...")
            exist,_,_ = VectorExtension.check_unique_id(value)
            if not exist:
                raise ValueError(f"ID column was not found in {value.file_name}.")

            if standard_vector is None:
                standard_vector = value
                continue

            if not VectorExtension.compare_vector_projection(standard_vector, value):
                is_same = False
                raise ValueError(f"The extend of {value.file_name} doesn't match {standard_vector.file_name}")

        return is_same
    
    @staticmethod
    def merge_vectors(vectors:list)->Vector:
        if vectors is None or len(vectors) == 0:
            raise ValueError("There is non vectors to merge.")
        
        if len(vectors) == 1:
            return vectors[0]
        
        wbe = WbEnvironment()
        out_att_fields = [AttributeField("id", FieldDataType.Int, 6, 0)]
        out_vector = wbe.new_vector(vectors[0].header.shape_type, out_att_fields, proj=vectors[0].projection)

        fid = 1
        for v in vectors:
            for i in range(v.num_records):
                geom = v[i]
                out_vector.add_record(geom) # Add the record to the output Vector
                out_vector.add_attribute_record([FieldData.new_int(fid)], deleted=False)
                fid = fid + 1

        return out_vector

    @staticmethod
    def save_vector(vector:Vector, destination_file:str):
        wbe = WbEnvironment()
        out_vector = wbe.new_vector(vector.header.shape_type, vector.get_attribute_fields(), proj=vector.projection)

        # Now fill it with the input data
        for i in range(vector.num_records):
            geom = vector[i]
            out_vector.add_record(geom) # Add the record to the output Vector
            out_vector.add_attribute_record(vector.get_attribute_record(i), deleted=False)
        # Finally, save the output file
        wbe.write_vector(out_vector, destination_file)

        #gpd.read_file(vector.file_name).to_file(destination_file)

    @staticmethod
    def check_field_in_vector(vector:Vector, field_name:str):
        """
        check if vector has attribute with given name
        """
        fields = [field.name for field in vector.get_attribute_fields() if field.name.lower() == field_name.lower()]     
        if len(fields) > 0:
            return True, fields[-1]
        else:
            return False, ""
        
    @staticmethod
    def vector_polygons_to_raster_with_boarder(polygon_vector:Vector, field_name:str, base_raster:Raster)->Raster:
        nodata = base_raster.configs.nodata
        rows = base_raster.configs.rows
        cols = base_raster.configs.columns

        wbe = WbEnvironment()
        polygon_raster = wbe.vector_polygons_to_raster(input = polygon_vector, field_name=field_name,base_raster=base_raster)
        boarder_raster = wbe.new_raster(base_raster.configs) 
        conflictWetlands = set()
        dX = [1, 1, 1, 0, -1, -1, -1, 0]
        dY = [-1, 0, 1, 1, 1, 0, -1, -1]

        for index in range(polygon_vector.num_records):
            #let's use wetland id here
            recNum = int(polygon_vector.get_attribute_value(index, field_name).get_value_as_f64())
            points = polygon_vector[index].points
            numPoints = len(points)
            partData = polygon_vector[index].parts
            numParts = len(partData)
            for part in range(numParts):
                startingPointInPart = partData[part]
                if part < numParts - 1:
                    endingPointInPart = partData[part + 1]
                else:
                    endingPointInPart = numPoints
                n = 0
                for i in range(startingPointInPart, endingPointInPart - 1):
                    x1 = base_raster.get_column_from_x(points[i].x)
                    y1 = base_raster.get_row_from_y(points[i].y)

                    x2 = base_raster.get_column_from_x(points[i+1].x)
                    y2 = base_raster.get_row_from_y(points[i+1].y)

                    d = 0

                    dy = abs(y2 - y1)
                    dx = abs(x2 - x1)

                    dy2 = dy << 1
                    dx2 = dx << 1

                    ix = 1 if x1 < x2 else -1
                    iy = 1 if y1 < y2 else -1

                    if dy <= dx:
                        while True:
                            if base_raster[y1, x1] != nodata:
                                if boarder_raster[y1, x1] > 0 and boarder_raster[y1, x1] != recNum:
                                    wetID = int(polygon_raster[y1, x1])
                                    if wetID > 0 and wetID not in conflictWetlands:
                                        conflictWetlands.add(wetID)
                                        for n in range(8):
                                            rowN = y1 + dY[n]
                                            colN = x1 + dX[n]
                                            neighbourID = int(polygon_raster[rowN, colN])
                                            if neighbourID > 0 and neighbourID != wetID:
                                                if neighbourID not in conflictWetlands:
                                                    conflictWetlands.add(neighbourID)
                                else:
                                    n += 1
                                    boarder_raster[y1, x1] = recNum
                            if x1 == x2:
                                break
                            x1 += ix
                            d += dy2
                            if d > dx:
                                y1 += iy
                                d -= dx2
                    else:
                        while True:
                            if base_raster[y1, x1] != nodata:
                                if boarder_raster[y1, x1] > 0 and boarder_raster[y1, x1] != recNum:
                                    wetID = int(polygon_raster[y1, x1])
                                    if wetID > 0 and wetID not in conflictWetlands:
                                        conflictWetlands.add(wetID)
                                        for n in range(8):
                                            rowN = y1 + dY[n]
                                            colN = x1 + dX[n]
                                            neighbourID = int(polygon_raster[rowN, colN])
                                            if neighbourID > 0 and neighbourID != wetID:
                                                if neighbourID not in conflictWetlands:
                                                    conflictWetlands.add(neighbourID)
                                else:
                                    n += 1
                                    boarder_raster[y1, x1] = recNum
                            if y1 == y2:
                                break
                            y1 += iy
                            d += dx2
                            if d > dy:
                                x1 += ix
                                d -= dy2

           
        for row in range(rows):
            for col in range(cols):
                if boarder_raster[row,col] == nodata and polygon_raster[row,col] != nodata:
                    boarder_raster[row,col] = polygon_raster[row,col]

        return boarder_raster


