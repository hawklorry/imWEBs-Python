# Upgrade the hydroclimate database to the latest structure.
# CAUTION: The existing data tables will be deleted. 

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Replace the database file path
# Make the backup before use this script
hydroclimate_database_file = r"C:\Work\imWEBs\test\Final_IMWEBs_Input_Package_Garvey Glenn\Hydroclimate.db3"

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

# %%
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
        return None

def run_sql(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)

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

        if data_type.upper() not in station_types:
            continue

        query = "SELECT Date, VALUE FROM " + table_name
        df_data = pd.read_sql_query(query,conn)
        df_data["STATION"] = station_id
        df_data.to_sql(f"STATION_DATA_{station_types[data_type.upper()]}",con = conn, if_exists='append',index=False)

        #delete old data table
        run_sql(conn, "DROP TABLE " + table_name)
                
    run_sql(conn, "DROP TABLE stations_old")

# %%
conn = create_connection(hydroclimate_database_file)

with conn:
    if conn is not None:
        run_sql(conn, sql_change_stations_table_name)
        run_sql(conn, sql_create_stations_table)

        #create table
        for t in station_data_tables:
            run_sql(conn, sql_create_station_data_table.replace("STATION_DATA_", t))

        #populate data
        populate_stations(conn)

        #create index for station column
        for t in station_data_tables:
            run_sql(conn, sql_create_station_data_table_index.replace("STATION_DATA_", t))

    

# %%
query = "SELECT DATE, VALUE FROM STATION_DATA_PCP where STATION=1" 
df_stations_data = pd.read_sql_query(query,conn, parse_dates=["DATE"], index_col="DATE")
df_stations_data.plot()

# %%



