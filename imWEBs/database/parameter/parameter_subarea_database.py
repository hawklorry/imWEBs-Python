from ..database_base import DatabaseBase

class ParameterSubareaDatabase(DatabaseBase):
    """Access to parameter_subarea database."""

    def __init__(self, database_file:str):
        super().__init__(database_file) 

 