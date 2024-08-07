import os

class IMWEBsException(Exception):
    def __init__(self, class_name, method_name, message):
        super().__init__(f"{class_name}.{method_name}: {message}")

class Utils:
    @staticmethod
    def check_path(path):
        return os.path.exists(path)

class WeightDataBase:
    def reset(self, weight_name):
        self.weight_name = weight_name
        self.m_rows = 0
        self.m_cols = 0
        self.m_data = []

class WeightDataFile(WeightDataBase):

    def __init__(self):
        super().__init__()

    def read_weight_from_txt_file(self, file_path, weight_name):
        # reset and check weight name
        self.reset(weight_name)

        # read data
        utils = Utils()

        weight_file_name = os.path.join(file_path, "")
        if not utils.check_path(file_path):
            raise IMWEBsException(self.__class__.__name__, self.read_weight_from_txt_file.__name__,
                                  f"The folder {weight_file_name} does not exist!")

        weight_file_name = os.path.join(weight_file_name, f"{weight_name}.txt")
        if not utils.check_path(weight_file_name):
            raise IMWEBsException(self.__class__.__name__, self.read_weight_from_txt_file.__name__,
                                  f"The file {weight_file_name} does not exist!")

        try:
            with open(weight_file_name, 'r') as fr:
                br = fr.readlines()

                # read header
                self.m_rows = int(float(br[0].strip()))
                self.m_cols = int(float(br[1].strip()))

                if self.m_rows <= 0 or self.m_cols <= 0:
                    raise IMWEBsException(self.__class__.__name__, self.read_weight_from_txt_file.__name__,
                                          f"The number of rows and columns of {weight_file_name} is not correct. They should be larger than 0. Please make sure the format is correct.")

                # initial
                self.m_data = [0.0] * (self.m_rows * self.m_cols)

                # read file
                for i in range(self.m_rows):
                    tokens = br[i + 2].strip().split()
                    for j in range(self.m_cols):
                        self.m_data[j + i * self.m_cols] = float(tokens[j])

        except IOError as e:
            raise IMWEBsException(self.__class__.__name__, self.read_weight_from_txt_file.__name__,
                                  "Something went wrong!")


