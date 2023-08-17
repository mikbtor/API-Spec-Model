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
