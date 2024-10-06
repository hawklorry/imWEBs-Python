from sqlalchemy import create_engine
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)


class DatabaseBase:
    def __init__(self, database_file):
        if not os.path.exists(database_file):
            raise ValueError(f"{database_file} doesn't exist.")
        
        self.database_file = database_file        
        self.engine = create_engine(f'sqlite:///{self.database_file}')  

    def read_distinct_list(self, table_name:str, column_name:str)->pd.DataFrame:
        """read distinct list of given column in given table"""
        return pd.read_sql(f"select distinct {column_name} from {table_name}", self.engine)

    def read_table(self, table_name:str)->pd.DataFrame:
        """read the whole table and return dataframe"""
        return pd.read_sql(f"select * from {table_name}", self.engine)

    def save_table(self, table_name:str, table_df:pd.DataFrame):
        table_df.to_sql(table_name, con = self.engine, if_exists='replace',index=False)

    def check_table_exist(self, table_name:str)->bool:
        return len(pd.read_sql(f"SELECT tbl_name FROM sqlite_master where type='table' and tbl_name ='{table_name}'",self.engine)) > 0 

    def populate_defaults(self, table_name:str):
        """
        populate table from csv file, used to load the default tables, assuming the table name is same as the csv file name
        """
        
        if self.check_table_exist(table_name):
            logger.info(f"Table {table_name} already exist, skip")
            return

        #try to find the corresponding csv file in the default folder
        csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults", f"{table_name}.csv")

        #raise error if the csv file doesn't exist
        if not os.path.exists(csv_file):
            raise ValueError(f"{csv_file} doesn't exist.")
        
        #load csv file and save to the database. It will replace the existing table.
        try:
            df = pd.read_csv(csv_file)
            df.to_sql(table_name, con = self.engine, if_exists='replace', index = False)
        except:
            raise ValueError(f"{csv_file} couldn't be imported to table {table_name} in database: {self.database_file}")
        