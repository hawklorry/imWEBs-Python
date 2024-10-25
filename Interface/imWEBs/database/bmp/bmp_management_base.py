class BMPManagementBase:
    def __init__(self):
        """Base class for all bmp management tables. They start with same columns."""
        self.Scenario = -1
        self.Location = -1 

class BMPManagementBaseWithYear(BMPManagementBase):
    """Base class for all bmp management tables. They start with same columns."""
    def __init__(self):
        super().__init__()
        self.Year = 1