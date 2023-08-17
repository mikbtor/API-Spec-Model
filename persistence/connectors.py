import uuid
from sqlite3 import Connection, Row, Cursor
from persistence.entities import Connector
import persistence.utils as ut 

def create_connector(f_db:str, c:Connector)->int:
    """
    Create an object in the t_object table
    :param o: Object to create
    :param f_out: Sparx DB file name
    :return: int
    """
    ea_guid = "{" + str(uuid.uuid1()) +"}"
    
    sql = ''' INSERT INTO t_connector(Direction, Connector_Type, SourceAccess, ea_guid, 
                                    DestCard, DestAccess, DestRole, Start_Object_ID, End_Object_ID, 
                                    Top_End_Label, Btm_End_Label) 
            VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    
    sql_vals =(c.direction, c.connector_type, "Public", ea_guid, c.dest_card, c.dest_access, c.dest_role, c.start_obj_id, c.end_obj_id, c.dest_role, c.dest_card )
    conn = ut.create_connection(f_db)   
    with conn:
        cur = conn.cursor()
        cur.execute(sql, sql_vals)
        conn.commit()
    return cur.lastrowid

def get_connectors_by_object(f_db:str, object_id:int, connector_type:str)->list:
    """
    Get the connectors for which the object is the source from the t_connector table
    :param f_db: name of database file
    :param object_id: object id value
    :return: dict
    """
    conn = ut.create_connection(f_db)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Connector_ID, Start_Object_ID, End_Object_ID, Connector_Type, DestRole, DestCard Type FROM t_connector where Start_Object_ID=? AND connector_type=?", (object_id, connector_type))
        rows = cur.fetchall()
        conns = list()
        for row in rows:
            c = Connector(row[0], row[1],row[2], row[3],row[4],row[5])
            conns.append(c) 
    return conns