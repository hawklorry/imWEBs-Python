import h5py
import os
import shutil
import subprocess
from ..names import Names

import logging
logger = logging.getLogger(__name__)

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

    @staticmethod
    def generate_parameter_h5(scenario_folder:str, output_folder:str):
        """
        generate parameter h5 file

        1. Assume all the weight files have been generated in output_folder
        2. run imwebsh5.exe tool to generate parameter.h5 in watershed/output folder
        3. move parameter.h5 to model folder
        4. clean weight files in watershed/output folder
        """

        if not os.path.exists(scenario_folder):
            raise ValueError(f"Couldn't find {scenario_folder}")
        
        if not os.path.exists(output_folder):
            raise ValueError(f"Couldn't find {output_folder}")
        
        #generate the parameter.h5
        imwebs_h5_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine", "imwebsh5.exe")
        if not os.path.exists(imwebs_h5_exe):
            raise ValueError(f"Couldn't find imwebsh5.exe.")        
        result = subprocess.run([imwebs_h5_exe] + [output_folder], capture_output=True, text=True)
        logger.info(result.stdout)
        logger.info(result.stderr)

        #check if parameter.h5 is generated
        if not os.path.exists(os.path.join(output_folder,Names.parameteH5Name)):
            raise ValueError("parameter.h5 is not generated")

        #copy parameter.h
        shutil.move(os.path.join(output_folder,Names.parameteH5Name),os.path.join(scenario_folder,Names.parameteH5Name))       


