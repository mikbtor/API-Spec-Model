import uuid
from sqlite3 import Connection, Row, Cursor
from persistence.entities import Object, Attribute, Connector, Enum
import persistence.utils as ut 

def create_attribute(f_db:str, object_id:int, name:str, type:str, position: int, is_collection: int)->int:
    """
    Create an object in the t_object table
    :param o: Object to create
    :param f_out: Sparx DB file name
    :return: int
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_attribute(Object_ID, ea_guid, Name, Scope, Type, IsCollection, Pos) VALUES(?,?,?,?,?,?,?) '''
        
    att =()
    
    with conn:
        cur = conn.cursor()
        ea_guid = "{" + str(uuid.uuid1()) +"}"
        scope = "Private"
        att =(object_id, ea_guid, name, scope, type, is_collection, position)
        cur.execute(sql, att)
        conn.commit()
    return cur.lastrowid

def create_enum_attribute(f_db:str, object_id:int, name:str, position: int)->int:
    """
    Create an object in the t_object table
    :param o: Object to create
    :param f_out: Sparx DB file name
    :return: int
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_attribute(Object_ID, ea_guid, Name, Pos, Stereotype)
              VALUES(?,?,?,?,?) '''
        
    att =()
    
    with conn:
        cur = conn.cursor()
        ea_guid = "{" + str(uuid.uuid1()) +"}"
        att =(object_id, ea_guid, name, position, "enum")
        cur.execute(sql, att)
        conn.commit()
    return object_id

def get_attributes_by_obj_id(f_db:str, object_id:int)->list:
    """
    Get the object's attributes from the t_attribute table
    :param f_in: name of database file
    :param object_id: object id value
    :return: dict
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT ID, Object_ID, Stereotype, Name, Type FROM t_attribute where Object_ID=?", (object_id,))
        rows = cur.fetchall()
        atts = list()
        for row in rows:
            att = Attribute(row[0], row[3],row[4])
            atts.append(att) 
    return atts