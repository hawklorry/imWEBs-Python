import os
from whitebox_workflows import WbEnvironment, Raster, Vector
from .vector_extension import VectorExtension

class FolderBase:
    def __init__(self, folder:str) -> None:
        self.folder = folder
        if not os.path.exists(self.folder):
            raise ValueError(f"Folder {folder} doesn't exist.")

        self.wbe = WbEnvironment()
        self.rasters = {}
        self.vectors = {}

    def get_file_path(self, filename:str)->str:
        return os.path.join(self.folder,filename)

    def save_raster(self, raster:Raster, file_name:str, overwrite = True):
        file_path = self.get_file_path(file_name)

        if os.path.exists(file_path) and not overwrite:
            raise ValueError(f"File: {file_path} already exists and overwrite is set to false.")
        
        self.wbe.write_raster(raster, file_path)        
        self.rasters[file_name] = raster

    def save_vector(self, vector:Vector, file_name:str, overwrite = True):
        file_path = self.get_file_path(file_name)

        if os.path.exists(file_path) and not overwrite:
            raise ValueError(f"File: {file_path} already exists and overwrite is set to false.")
        
        VectorExtension.save_vector(vector, self.get_file_path(file_name))      
        self.vectors[file_name] = vector

    def find_file(self, filename:str)->str:        
        file_path = os.path.join(self.folder,filename)
        if os.path.exists(file_path):
            return file_path
        
        return None
    
    def get_raster(self, raster_name:str)->Raster:
        """get raster with the given name. if the raster doesn't exist, return none."""
        if raster_name in self.rasters:
            return self.rasters[raster_name]
        else:
            file_name = self.find_file(raster_name)
            if file_name is not None:
                self.rasters[raster_name] = self.wbe.read_raster(file_name)
                return self.rasters[raster_name] 
        
        return None
    
    def get_vector(self, shapefile_name:str)->Vector:
        """get vector with the given name. if the vector doesn't exist, return none."""
        if shapefile_name in self.vectors:
            return self.vectors[shapefile_name]
        else:
            file_name = self.find_file(shapefile_name)
            if file_name is not None:
                self.rasters[shapefile_name] = self.wbe.read_vector(file_name)
                return self.rasters[shapefile_name] 
        
        return None           