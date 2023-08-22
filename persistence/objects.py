import uuid
from sqlite3 import Connection, Row, Cursor
from persistence.entities import Object, Attribute, Connector, Enum
import persistence.utils as ut  


def get_objects_in_package(f_db:str, package_id:int, object_type:str, stereotype:str)->dict:
    """
    Get the objects of a package from the t_object table of a given object_type and stereotype
    :param conn: the Connection object
    :param package_id: package id
    :return: dict
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Object_ID, Package_ID, ParentID, Object_Type, Stereotype, Name, Note   FROM t_object where Package_ID=? AND Object_Type=? AND Stereotype=?", (package_id,object_type, stereotype))
        rows = cur.fetchall()
        objs = dict()
        for row in rows:
            o = Object(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            objs[row[0]] = o 
    return objs

def get_enums_in_package(f_db:str, package_id:int)->list:
    """
    Get the enums of a package from the t_object table
    :param conn: the Connection object
    :param package_id: package id
    :return: dict
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Object_ID, Package_ID, ParentID, Object_Type, Name, Note   FROM t_object where Package_ID=? AND Object_Type=? ", (package_id,"Enumeration"))
        rows = cur.fetchall()
        objs = list()
        for row in rows:
            o = Enum(row[0],row[1],row[2],row[3],row[4],row[5])
            objs.append(o) 
    return objs

def get_object_by_id(f_db:str, object_id:int)->Object:
    """
    Get the object with the given id from the t_object table
    :param f_db: name of database file
    :param object_id: object id value
    :return: object
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Object_ID, Package_ID, ParentID, Object_Type, Stereotype, Name, Note FROM t_object where Object_ID=?",(object_id,))
        row = cur.fetchone()
        if row is not None: 
            o = Object(row[0],row[1],row[2],row[3], row[4],row[5], row[6])
            return o    
        else:
            return None
    

def get_object_by_name(f_db:str, name:str)->Object:
    """
    Get the object with the given id from the t_object table
    :param f_db: name of database file
    :param object_id: object id value
    :return: object
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Object_ID, Package_ID, ParentID, Object_Type, Stereotype, Name, Note FROM t_object where Name=? ",(name, ))
        row = cur.fetchone()
        if row is not None: 
            o = Object(row[0],row[1],row[2],row[3], row[4],row[5], row[6])
            return o
        else:
            return None

def create_object(f_db:str, package_id:int, type:str, stereotype:str, name:str)->int:
    """
    Create an object in the t_object table
    :param o: Object to create
    :param f_out: Sparx DB file name
    :return: int
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_object(Package_ID, ea_guid, Object_Type, Stereotype, Name, Author, Status, Abstract, Scope, Complexity, Effort, ParentID)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    
    # Primary key is auto-incremented
    
    obj =()
    
    with conn:
        cur = conn.cursor()
        ea_guid = "{" + str(uuid.uuid1()) +"}"
        obj =(package_id, ea_guid, type, stereotype, name, "DrM", "Proposed", 0, "Public",1,0,0)
        cur.execute(sql, obj)
        conn.commit()
    return cur.lastrowid