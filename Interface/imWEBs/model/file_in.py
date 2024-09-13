from datetime import date
import os

class FileIn:
    def __init__(self, 
                 folder:str,
                 cell_size:int, 
                 cell_num:int, 
                 subarea_num:int, 
                 subbasin_num:int, 
                 start_date:date, 
                 end_date:date,
                 data_type_station_ids:dict,
                 interval:str = "Daily") -> None:
        self.folder = folder
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
            f.writelines(f"VERSIONTYPE|1")
            f.writelines(f"ISPREPAREFORSUBAREAINPUT|0")
            f.writelines(f"CELLSIZE|{self.cell_size}")
            f.writelines(f"CELLNUMBER|{self.cell_num}")
            f.writelines(f"SUBAREANUMBER|{self.subarea_num}")
            f.writelines(f"SUBBASINCOUNT|{self.subbasin_num}")
            f.writelines(f"INTERVAL|{self.interval}")
            f.writelines(f"STARTTIME|{self.start_date.strftime("%Y/%m/%d")}")
            f.writelines(f"ENDTIME|{self.end_date.strftime("%Y/%m/%d")}")

            for data_type, ids in self.data_type_station_ids.items():
                f.writelines(f"SITECOUNT|{len(ids)}|{data_type}")
                for id in ids:
                    f.writelines(f"SITENAME|{id}|{data_type}")

            

