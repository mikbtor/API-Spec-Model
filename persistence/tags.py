import uuid
from sqlite3 import Connection, Row, Cursor
from persistence.entities import Tag
import persistence.utils as ut

def get_object_tags(f_in:str, object_id:str) ->dict:
    """
    Get the tags (properties) of an object with the given id from t_objectproperties
    :param f_in: the database file name
    :param object_id: object id value
    :return:
    """
    tags = dict()
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT PropertyID, Object_ID, Property, Value FROM t_objectproperties where Object_ID=?",(object_id,))
        rows = cur.fetchall()
        for row in rows: 
            tags[row[2]] = row[3] 
    return tags
        

def get_attribute_tags(f_in:str, attribute_id:int)->dict:
    """
    Get the tags (properties) of an attribute with the given id from t_attributetag
    :param f_in: the database file name
    :param attribute_id: attribute id
    :return: dict
    """
    tags = dict()
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT PropertyID, ElementID, Property, VALUE FROM t_attributetag where ElementID=?",(attribute_id,))
        rows = cur.fetchall()
        for row in rows:
            tags[row[2]] = row[3] 
    return tags

def create_obj_tag(f_db:str, object_id:int, name:str, value:str, notes: str)->int:
    """
    Create a tag in the t_objectproperties table
    :param f_db: Sparx DB file name
    :param object_id: Object id
    :param name: name of tag
    :param value: type of attribute
    :param notes: notes, e.g. 'Default: /'
    :return: int: tag identifier
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_objectproperties(Object_ID, ea_guid, Property, Value, Notes) VALUES(?,?,?,?,?) '''
    ea_guid = "{" + str(uuid.uuid1()) +"}"
    sql_vals =(object_id, ea_guid, name, value, notes)    
    with conn:
        cur = conn.cursor()
        cur.execute(sql, sql_vals)
        conn.commit()
    return cur.lastrowid

def create_att_tag(f_db:str, att_id:int, name:str, value:str, notes: str)->int:
    """
    Create a tag in the t_objectproperties table
    :param f_db: Sparx DB file name
    :param object_id: Object id
    :param name: name of tag
    :param value: type of attribute
    :param notes: notes, e.g. 'Default: /'
    :return: int: tag identifier
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_attributetag(ElementID, ea_guid, Property, VALUE, NOTES) VALUES(?,?,?,?,?) '''
    ea_guid = "{" + str(uuid.uuid1()) +"}"
    sql_vals =(att_id, ea_guid, name, value, notes)    
    with conn:
        cur = conn.cursor()
        cur.execute(sql, sql_vals)
        conn.commit()
    return cur.lastrowid
