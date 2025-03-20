from ..database_base import DatabaseBase
import pandas as pd
import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from .stations import Stations

class HydroClimateDatabase(DatabaseBase):
    """
    Hydroclimate database
    """

    columns_measured_data = ["DATE", "FLOW","SEDIMENT","ORGANICN","ORGANICP","NO3","NH3","NO2","MINERALP"]

    def __init__(self, database_file):
        super().__init__(database_file)    

        self.__station_coordinates = {}
        self.__data_type_station_ids_dictionary = {}

    def validate_measured_data_table(self,table_name:str):
        self.check_table(table_name, HydroClimateDatabase.columns_measured_data)

    @property
    def station_coordinates(self)->dict:
        """Coordinates of all stations. Used for interpolation"""
        if len(self.__station_coordinates) <= 0:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                select_stmt = select(Stations)
                for row in session.scalars(select_stmt):
                    self.__station_coordinates[row.ID] = (row.XPR, row.YPR)

        return self.__station_coordinates
    
    @property
    def data_type_station_ids_dictionary(self):
        """The station data type and number of stations"""
        if len(self.__data_type_station_ids_dictionary) <= 0:
            for data_type, table_appendix in HydroClimateDatabase.station_types.items():
                table_name = f"STATION_DATA_{table_appendix}"
                station_id_df = self.read_distinct_list(table_name, "STATION")
                if len(station_id_df) > 0:
                    self.__data_type_station_ids_dictionary[data_type] = station_id_df["STATION"].to_list()

        return self.__data_type_station_ids_dictionary
    
    @property
    def data_start_date(self)->pd.Timestamp:
        """The start date considering all data type"""
        start_date = pd.Timestamp('1900-01-01')
        for _, table_appendix in HydroClimateDatabase.station_types.items():
            table_name = f"STATION_DATA_{table_appendix}"
            start_date_df = pd.read_sql(f"select min(datetime(date)) start_date from {table_name}", self.engine)
            if len(start_date_df) > 0:
                data_type_start_date = pd.to_datetime(start_date_df['start_date'].to_list()[0])
                if data_type_start_date > start_date:
                    start_date = data_type_start_date

        return start_date

    @property
    def data_end_date(self)->pd.Timestamp:
        """The end date considering all data type"""
        end_date = pd.Timestamp('2100-01-01')
        for _, table_appendix in HydroClimateDatabase.station_types.items():
            table_name = f"STATION_DATA_{table_appendix}"
            end_date_df = pd.read_sql(f"select max(datetime(date)) end_date from {table_name}", self.engine)
            if len(end_date_df) > 0:
                data_type_end_date = pd.to_datetime(end_date_df['end_date'].to_list()[0])
                if data_type_end_date < end_date:
                    end_date = data_type_end_date

        return end_date


#region Migration

    sql_change_stations_table_name = """
        ALTER TABLE stations
        RENAME TO stations_old;
    """

    sql_create_stations_table = """
        CREATE TABLE IF NOT EXISTS STATIONS (
            ID INTEGER PRIMARY KEY,
            NAME TEXT NOT NULL,
            XPR  REAL,
            YPR  REAL,
            LAT  REAL,
            LONG REAL,
            ELEVATION REAL,
            AREA REAL
        );
        """

    sql_create_station_data_table = """
        CREATE TABLE IF NOT EXISTS STATION_DATA_ (
            ID INTEGER PRIMARY KEY,
            STATION INTEGER NOT NULL,
            DATE  TEXT NOT NULL,
            VALUE REAL NOT NULL,
            FOREIGN KEY (STATION) REFERENCES STATIONS (ID)
        );
        """

    sql_create_station_data_table_index = """
        CREATE INDEX IDX_STATION_DATA_ ON STATION_DATA_ (STATION);
    """

    station_data_tables = [
    "STATION_DATA_PCP",
    "STATION_DATA_TMX",
    "STATION_DATA_TMN",
    "STATION_DATA_SLR",
    "STATION_DATA_HMD",
    "STATION_DATA_WDIR",
    "STATION_DATA_WSPD"
    ]

    station_types = {
    "P":"PCP",
    "TMAX":"TMX",
    "TMIN":"TMN",
    "RM":"HMD",
    "SR":"SLR",
    "WS":"WSPD",
    "WD":"WDIR"
    }


    @staticmethod
    def run_sql(conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Exception as e:
            print(e)

    @staticmethod
    def populate_stations(conn):
        #populate the new stations table
        query = "SELECT DISTINCT NAME,XPR,YPR,LAT,LONG,ELEVATION,AREA FROM STATIONS_OLD"
        df_stations = pd.read_sql_query(query,conn)
        df_stations["ID"] = df_stations.index + 1
        df_stations.to_sql(f"STATIONS",con = conn, if_exists='append', index=False)

        #populate the station data
        query = "SELECT NAME,TYPE,TABLENAME FROM STATIONS_OLD"
        df_stations_table = pd.read_sql_query(query,conn)
        for index in df_stations_table.index:
            station_name = df_stations_table.loc[index]["NAME"]       
            station_id = df_stations[df_stations["NAME"] == station_name].iloc[0]["ID"]
            data_type = df_stations_table.loc[index]["TYPE"]
            table_name = df_stations_table.loc[index]["TABLENAME"]

            print(f"{station_name} - {data_type} - {table_name}")

            if data_type.upper() not in HydroClimateDatabase.station_types:
                continue

            query = "SELECT Date, VALUE FROM " + table_name
            df_data = pd.read_sql_query(query,conn)
            df_data["STATION"] = station_id
            df_data.to_sql(f"STATION_DATA_{HydroClimateDatabase.station_types[data_type.upper()]}",con = conn, if_exists='append',index=False)

            #delete old data table
            HydroClimateDatabase.run_sql(conn, "DROP TABLE " + table_name)
                    
        HydroClimateDatabase.run_sql(conn, "DROP TABLE stations_old")

    @staticmethod
    def migrate(hydroclimate_database_file:str):
        """Migrate the hydroclimate data from old format where the data was stored in separated tables to new format."""

        conn = sqlite3.connect(hydroclimate_database_file)

        with conn:
            if conn is not None:
                HydroClimateDatabase.run_sql(conn, HydroClimateDatabase.sql_change_stations_table_name)
                HydroClimateDatabase.run_sql(conn, HydroClimateDatabase.sql_create_stations_table)

                #create table
                for t in HydroClimateDatabase.station_data_tables:
                    HydroClimateDatabase.run_sql(conn, HydroClimateDatabase.sql_create_station_data_table.replace("STATION_DATA_", t))

                #populate data
                HydroClimateDatabase.populate_stations(conn)

                #create index for station column
                for t in HydroClimateDatabase.station_data_tables:
                    HydroClimateDatabase.run_sql(conn, HydroClimateDatabase.sql_create_station_data_table_index.replace("STATION_DATA_", t))


#endregion