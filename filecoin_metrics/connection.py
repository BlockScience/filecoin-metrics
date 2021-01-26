
def get_connection_string() -> str:
    # Prepare SQL connection string to be used on the functions
    CONN_STRING_PATH = '../config/sentinel-conn-string.txt'

    with open(CONN_STRING_PATH, 'r') as fid:
        conn_string = fid.read()
    return conn_string