from sqlite3 import Connection, Row, Cursor
from persistence.entities import Package
import persistence.utils as ut

def get_package(f_in:str, package_guid:str)->Package:
    """
    Query all rows in the t_package table
    :param conn: the Connection object
    :param package_guid: ea_guid value
    :return:
    """
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Package_ID, Parent_ID, ea_guid, Name FROM t_package where ea_guid=?",(package_guid,))
        row = cur.fetchone()
        if row is not None:
            p = Package(row[0],row[1],row[2],row[3])
            return p
        else:
            return None    

def get_child_packages(f_in:str, package_id:int)->dict:
    """
    Get the child packages from the t_package table
    :param conn: the Connection object
    :param package_id: package id
    :return:
    """
    packs = dict()
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Package_ID, Parent_ID, ea_guid, Name  FROM t_package where Parent_ID=?", (package_id,))
        rows = cur.fetchall()
        for row in rows:
            p = Package(row[0],row[1],row[2],row[3])
            packs[row[0]] = p 
    return packs





