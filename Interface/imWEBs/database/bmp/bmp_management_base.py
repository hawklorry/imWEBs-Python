from ...bmp.bmp_type import DefaultScenarioId

class BMPManagementBase:
    def __init__(self):
        """Base class for all bmp management tables. They start with same columns."""
        self.Scenario = DefaultScenarioId
        self.Location = -1 

class BMPManagementBaseWithYear(BMPManagementBase):
    """Base class for all bmp management tables. They start with same columns."""
    def __init__(self):
        super().__init__()
        self.Year = 1