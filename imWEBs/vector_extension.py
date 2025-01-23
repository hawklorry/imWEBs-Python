from whitebox_workflows import WbEnvironment, Vector, AttributeField, FieldDataType, FieldData, Raster, VectorGeometryType
from io import StringIO
import pandas as pd
import geopandas as gpd
from .names import Names
import os
import shutil

import logging
logger = logging.getLogger(__name__)

class VectorExtension:

    @staticmethod
    def vector_to_raster(vector:Vector, base_raster:Raster)->Raster:
        wbe = WbEnvironment()
        exist, id_field_name = VectorExtension.check_id(vector)
        if not exist:
            raise ValueError(f"Couldn't find id field in {vector.file_name}.")

        if vector.header.shape_type == VectorGeometryType.Polygon or vector.header.shape_type == VectorGeometryType.PolygonM or vector.header.shape_type == VectorGeometryType.PolygonZ:
            return wbe.vector_polygons_to_raster(input = vector, field_name = id_field_name, base_raster = base_raster)
        elif vector.header.shape_type == VectorGeometryType.Point or vector.header.shape_type == VectorGeometryType.PointM or vector.header.shape_type == VectorGeometryType.PointZ:
            return wbe.vector_points_to_raster(input = vector, field_name = id_field_name, base_raster = base_raster)
        else:
            raise ValueError(f"Wrong shape type with {vector.file_name}.")

    @staticmethod
    def add_id_for_raster_value(vector:Vector, use_fid = False)->Vector:
        if len([field.name for field in vector.get_attribute_fields() if field.name == Names.field_name_raster_value]) <= 0:
            return vector

        id_field = AttributeField(Names.field_name_id, FieldDataType.Int, 10, 0)
        vector.add_attribute_field(id_field)

        for i in range(vector.num_records):
            if use_fid:
                vector.set_attribute_value(i,Names.field_name_id,FieldData.new_int(i+1))
            else:
                value = vector.get_attribute_value(i, Names.field_name_raster_value).get_value_as_f64()
                vector.set_attribute_value(i,Names.field_name_id,FieldData.new_int(int(value)))
        return vector
    
    @staticmethod
    def join_two_vector(vector1:Vector, vector2:Vector, foreign_key1:int, copied_fields_from_vector2:list[str])->Vector:
        """
        Join vector1 and vector2 over foreign_key1 in vector1 and id in vector2 and copy the fields from vector2
        """
        vector2_fields = vector2.get_attribute_fields()
        vector2_fields = {field.name:field for field in vector2_fields}
        vector2_values = {}
        for col in copied_fields_from_vector2:
            if col not in vector2_fields:
                raise ValueError(f"Coundn't find column {col} in {vector2.file_name}")
            values = VectorExtension.get_unique_field_value(vector2, col, int if vector2_fields[col].field_type == FieldDataType.Int else float)
            vector2_values[col] = values

        #add the columns
        for col in copied_fields_from_vector2:
            field = None
            if vector2_fields[col].field_type == FieldDataType.Int:
                field = AttributeField(col, FieldDataType.Int, 10, 0)
            else:
                field = AttributeField(col, FieldDataType.Real, 8, 3)
            vector1.add_attribute_field(field)

        #assign the values
        for i in range(vector1.num_records):
            foreign_key = int(vector1.get_attribute_value(i, foreign_key1).get_value_as_f64())

            for col in copied_fields_from_vector2:
                if vector2_fields[col].field_type == FieldDataType.Int:
                    vector1.set_attribute_value(i,col,FieldData.new_int(vector2_values[col][foreign_key]))
                else:
                    vector1.set_attribute_value(i,col,FieldData.new_real(vector2_values[col][foreign_key]))
        return vector1            


    @staticmethod
    def decompsite_overlay_id(vector:Vector, old_id_to_new_id_dict:dict[int, int], name1:str, name2:str, raster1_max:int)->Vector:
        field1 = AttributeField(name1, FieldDataType.Int, 10, 0)
        field2 = AttributeField(name2, FieldDataType.Int, 10, 0)
        vector.add_attribute_field(field1)
        vector.add_attribute_field(field2)

        new_id_to_old_id_dict = {value: key for key, value in old_id_to_new_id_dict.items()}

        for i in range(vector.num_records):
            new_id = int(vector.get_attribute_value(i, Names.field_name_id).get_value_as_f64())
            old_id = new_id_to_old_id_dict[new_id]
            id1 = int(old_id % raster1_max)
            id2 = int((old_id - id1) / raster1_max)
            vector.set_attribute_value(i,name1,FieldData.new_int(id1))
            vector.set_attribute_value(i,name2,FieldData.new_int(id2))
        return vector       

    @staticmethod
    def get_unique_ids(vector:Vector)->list:
        if vector is None:
            return []
        
        exist, _, ids = VectorExtension.check_unique_id(vector)
        if exist:
            return ids
        return []
    

    @staticmethod
    def get_unique_field_value(vector:Vector, field_name:str, type:type = int)->dict:
        exist, name = VectorExtension.check_field_in_vector(vector, field_name)

        if not exist:
            raise ValueError(f"Can't find field {field_name} in {vector.file_name}.")
        
        exist_id,field_name_id = VectorExtension.check_id(vector)
        
        field_values = {}
        for i in range(vector.num_records):
            id = int(vector.get_attribute_value(i, field_name_id).get_value_as_f64())
            field_value = vector.get_attribute_value(i, name)
            if not field_value.is_null():
                if type is int:
                    if int(field_value.get_value_as_f64()) > 0:
                        field_values[id] = int(field_value.get_value_as_f64())
                elif type is str:
                    if(len(field_value.get_as_string()) > 0):
                        field_values[id] = field_value.get_as_string()
                elif type is float:
                    field_values[id] = field_value.get_value_as_f64()

        return field_values

    @staticmethod
    def check_id(vector:Vector):
        """check if the vector has ID column"""
        if vector is None:
            return False, ""

        field_names = [field.name.lower() for field in vector.get_attribute_fields()]
        if Names.field_name_id not in field_names:
            return False, ""
        
        field_index = field_names.index(Names.field_name_id)
        field_name = vector.get_attribute_fields()[field_index].name
        return True, field_name

    @staticmethod
    def check_unique_id(vector:Vector):
        """check if the the vector has the ID column and values are unique"""        
        exist,field_name = VectorExtension.check_id(vector)
        if not exist:
            return False, "", []
        
        ids = []
        for i in range(vector.num_records):
            field_data = vector.get_attribute_value(i, field_name)
            if field_data.is_null():
                raise ValueError(f"The id in {vector.file_name} can't be null.")
            id = int(field_data.get_value_as_f64())
            if id in ids:
                return False, "", []
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
                raise ValueError(f"ID column was not found in {value.file_name} or the ids are not unique.")

            if standard_vector is None:
                standard_vector = value
                continue

            if not VectorExtension.compare_vector_projection(standard_vector, value):
                is_same = False
                raise ValueError(f"The projection of {value.file_name} doesn't match {standard_vector.file_name}. Please check shapefile projection.")

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
        if os.path.exists(vector.file_name):
            shutil.copyfile(vector.file_name, destination_file)
            shutil.copyfile(vector.file_name.lower().replace(".shp",".prj"), destination_file.lower().replace(".shp",".prj"))
            shutil.copyfile(vector.file_name.lower().replace(".shp",".dbf"), destination_file.lower().replace(".shp",".dbf"))
            shutil.copyfile(vector.file_name.lower().replace(".shp",".shx"), destination_file.lower().replace(".shp",".shx"))
        else:
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
    def check_fields_in_vector(vector:Vector, field_names:list):
        """check if vector has list of fields"""
        for field in field_names:
            if not VectorExtension.check_field_in_vector(vector, field)[0]:
                raise ValueError(f"Couldn't find column {field} in {vector.file_name}. It should have following columns: {", ".join(list)}.")
        
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


