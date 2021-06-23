# import libraries
from sqlalchemy import create_engine
import pandas as pd


# load connection string
CONN_STRING_PATH = 'sentinel_conn_string_andrew.txt'

with open(CONN_STRING_PATH, 'r') as fid:
    conn_string = fid.read()
    
# create database connection.
connection = create_engine(conn_string, pool_recycle=3600).connect()

QUERY = """
SELECT 
*
FROM messages
ORDER BY
height DESC
"""

messages = (pd.read_sql(QUERY, connection))

messages.to_parquet('messages.parquet.gzip',compression='gzip')