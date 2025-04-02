from ...bmp.bmp_type import DefaultScenarioId

class BMPManagementBase:
    def __init__(self, location:int = -1):
        """Base class for all bmp management tables. They start with same columns."""
        self.Scenario = DefaultScenarioId
        self.Location = location 

class BMPManagementBaseWithYear(BMPManagementBase):
    """Base class for all bmp management tables. They start with same columns."""
    def __init__(self, location: int = -1, year:int = 1):
        super().__init__(location)
        self.Year = year