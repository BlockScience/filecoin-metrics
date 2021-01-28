from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

def get_connection_string(path: str=None) -> str:
    # Prepare SQL connection string to be used on the functions
    if path is None:
        path = '../config/sentinel-conn-string.txt'


    with open(path, 'r') as fid:
        conn_string = fid.read()
    return conn_string


def get_connection(conn_string: str=None) -> Engine:
    if conn_string is None:
        conn_string = get_connection_string()
    connection = create_engine(conn_string, pool_recycle=3600).connect()
    return connection
