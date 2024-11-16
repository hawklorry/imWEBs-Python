import pandas as pd
import os

class FileIn:
    def __init__(self, 
                 folder:str,
                 model_type:str,
                 cell_size:int, 
                 cell_num:int, 
                 subarea_num:int, 
                 subbasin_num:int, 
                 start_date:pd.Timestamp, 
                 end_date:pd.Timestamp,
                 data_type_station_ids:dict,
                 interval:str = "Daily") -> None:
        self.folder = folder
        self.model_type = model_type
        self.cell_size = cell_size
        self.cell_num = cell_num
        self.subarea_num = subarea_num
        self.subbasin_num = subbasin_num
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.data_type_station_ids = data_type_station_ids
        

    def write_file(self):
        with open(os.path.join(self.folder, "file.in"),'w') as f:
            if self.model_type == "subarea":
                f.writelines(f"VERSIONTYPE|1")
            else:
                f.writelines(f"VERSIONTYPE|0")

            f.writelines(f"\nISPREPAREFORSUBAREAINPUT|0")
            f.writelines(f"\nCELLSIZE|{self.cell_size}")
            f.writelines(f"\nCELLNUMBER|{self.cell_num}")
            f.writelines(f"\nSUBAREANUMBER|{self.subarea_num}")
            f.writelines(f"\nSUBBASINCOUNT|{self.subbasin_num}")
            f.writelines(f"\nINTERVAL|{self.interval}")
            f.writelines(f"\nSTARTTIME|{self.start_date.strftime("%Y/%m/%d")}")
            f.writelines(f"\nENDTIME|{self.end_date.strftime("%Y/%m/%d")}")

            for data_type, ids in self.data_type_station_ids.items():
                f.writelines(f"\nSITECOUNT|{len(ids)}|{data_type}")
                for id in ids:
                    f.writelines(f"\nSITENAME|{id}|{data_type}")

            

