from ...bmp.bmp_type import BMPType, DefaultScenarioId

class BMP_scenarios:
    def __init__(self, bmp_type:BMPType, distribution:str, parameter:str):
        self.ID = DefaultScenarioId
        self.NAME = "scenario"
        self.BMP = bmp_type.value
        self.DISTRIBUTION = distribution
        self.PARAMETER = parameter

        