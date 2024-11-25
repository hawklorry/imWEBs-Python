import json
from ..outputs import Outputs
from ..names import Names
import os
import subprocess

import logging
logger = logging.getLogger(__name__)

class ParameterSubarea:
    def __init__(self, outputs:Outputs):
        self.outputs = outputs
        self.climate_type_name = {1:"p", 2:"t",4:"rm",5:"sr", 6:"w",8:"pet"}

    def generate(self):
        logger.info(f"Creating {Names.parameterSubareaDatabaseName} ...")

        self.__create_appsetting_json()
        self.__run_imwebs_input_tool("base-conversion-all")
        self.__run_imwebs_input_tool("bmp-conversion-all")

    def __get_imwebs_input_tool_folder(self)->str:
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imwebs_input_tool")
        if not os.path.exists(folder):
            raise ValueError(f"Coundn't find {folder}.")
        return folder

    def __create_appsetting_json(self):
        """Create appsettings.json to used with imWEBsInputTool"""

        data = {}

        #log setting
        data["Serilog"] = {"MinimumLevel" : "Debug"} 
        
        console_output = {}
        console_output["Name"] = "Console"
        console_output["Args"] = {"outputTemplate": "===> {Timestamp:HH:mm:ss.fff zzz} [{Level:w3}] {Message:lj}{NewLine}{Exception}"}
        data["Serilog"]["WriteTo"] = [console_output]

        #outputs
        data["Outputs"] = {"OutputDbPath": os.path.join(self.outputs.database_folder, Names.parameterSubareaDatabaseName)}

        #inputs
        data["Inputs"] = {"BmpDbPath": os.path.join(self.outputs.database_folder, Names.bmpDatabaseName)}
        data["Inputs"]["HydroClimateDbPath"] = os.path.join(self.outputs.database_folder, Names.hydroclimateDatabasename)
        data["Inputs"]["ParameterDbPath"] = os.path.join(self.outputs.database_folder, Names.parameterDatabaseName)
        data["Inputs"]["WeightInputs"] = []

        for type_id, type_name in self.climate_type_name.items():
            weight_file = os.path.join(self.outputs.folder, f"weight_{type_name}.txt")
            if os.path.exists(weight_file):
                weight = {"ClimateDateTypeId": type_id}
                weight["WeightFilePath"] = weight_file
                weight["Seperator"] = "\t"
                data["Inputs"]["WeightInputs"].append(weight)

        #write to appsettings.json
        imwebs_input_tool_appsettings_json = os.path.join(self.__get_imwebs_input_tool_folder(), "appsettings.json")
        with open(imwebs_input_tool_appsettings_json, 'w') as file: 
            json.dump(data, file, indent=2)

    def __run_imwebs_input_tool(self, parameter):
        """Run imwebs input tool with given parameter"""
        imwebs_input_tool_exe = os.path.join(self.__get_imwebs_input_tool_folder(), "ImwebsSubarea.Input.CLI.exe")
        if not os.path.exists(imwebs_input_tool_exe):
            raise ValueError(f"Couldn't find ImwebsSubarea.Input.CLI.exe.")     
           
        result = subprocess.run([imwebs_input_tool_exe] + [parameter], capture_output=True, text=True)
        if len(result.stdout) > 0:
            logger.info(result.stdout)        
        if len(result.stderr) > 0:
            logger.info(result.stderr)