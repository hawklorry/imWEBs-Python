from ...bmp.bmp_type import BMPType

class BMP_scenarios:
    def __init__(self, bmp_type:BMPType, distribution:str, parameter:str):
        self.ID = -1
        self.NAME = "scenario"
        self.BMP = bmp_type.value
        self.DISTRIBUTION = distribution
        self.PARAMETER = parameter

        