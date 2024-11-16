import os

class FileOut:
    def __init__(self, folder) -> None:
        self.folder = folder

    def write_file(self):
        """Use empty output file for now"""
        with open(os.path.join(self.folder, "file.out"),'w') as f:
            f.writelines("OUTPUTTYPE | 1")