from sqlalchemy import create_engine

class DatabaseBase:
    def __init__(self, database_file):
        self.database_file = database_file        
        self.engine = create_engine(f'sqlite:///{self.database_file}')     