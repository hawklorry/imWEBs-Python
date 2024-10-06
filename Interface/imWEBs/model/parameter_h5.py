import h5py
import os

class ParameterH5:
    def __init__(self, parameter_h5_file) -> None:
        if not os.path.exists(parameter_h5_file):
            raise ValueError(f"{parameter_h5_file} doesn't exist.")
        
        self.parameter_h5_file = parameter_h5_file      
        with h5py.File(parameter_h5_file, 'r') as h5_file:
            for group_name in h5_file.keys():
                if group_name == "asc":
                    group = h5_file[group_name]
                    for attr_name, attr_value in group.attrs.items():
                        if attr_name == "CELL_SIZE":
                            self.cell_num = int(attr_value[0])
                        if attr_name == "DX":
                            self.cell_size = attr_value[0]
