import uuid
from sqlite3 import Connection, Row, Cursor
from persistence.entities import Object, Attribute, Connector, Enum
import persistence.utils as ut 

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

def create_attribute(f_db:str, object_id:int, name:str, type:str, position: int, is_collection: int, is_required:int)->int:
    """
    Create an attribute in the t_attribute table
    :param f_db: Sparx DB file name
    :param object_id: Object id
    :param name: name of attribute
    :param type: type of attribute
    :param position: position of attribute
    :is_collection: integer 0 - not a collection, 1 - it is a collection
    :is_required: integer 0 - not required, 1 - required
    :return: int
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_attribute(Object_ID, ea_guid, Name, Scope, Type, Stereotype, IsCollection, Pos) VALUES(?,?,?,?,?,?,?,?) '''
        
    ea_guid = "{" + str(uuid.uuid1()) +"}"
    scope = "Private"
    if is_required == 1:
        stereotype = "required"
    else:
        stereotype = None
    att =(object_id, ea_guid, name, scope, type, stereotype, is_collection, position)
    
    with conn:
        cur = conn.cursor()
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
        
    ea_guid = "{" + str(uuid.uuid1()) +"}"
    att =(object_id, ea_guid, name, position, "enum")
    
    with conn:
        cur = conn.cursor()
        cur.execute(sql, att)
        conn.commit()
    return cur.lastrowid

