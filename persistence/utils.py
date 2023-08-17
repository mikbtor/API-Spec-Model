import sqlite3
from sqlite3 import Error, Connection

def create_connection(db_file:str)->Connection:
    """ 
    Create a database connection to the SQLite database
    specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn