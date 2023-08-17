from persistence.entities import Operation, Parameter
import persistence.utils as ut

def get_operations(f_in:str, object_id:int)->dict:
    """
    Get the operations of an object with the given id from t_operations
    :param f_in: the database file name
    :param object_id: object id value
    :return:
    """
    ops = dict()
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT OperationID, Object_ID, Stereotype, Name, Type, ReturnArray, Notes FROM t_operation where Object_ID=?",(object_id,))
        rows = cur.fetchall()
        for row in rows: 
            o = Operation(row[0],row[1],row[2],row[3], row[4],row[5],row[6])
            ops[row[0]] = o
    return ops

def get_operation_parameters(f_in: str, operation_id:int)->list:
    """
    Get the operations of an object with the given id from t_operations
    :param f_in: the database file name
    :param object_id: object id value
    :return:
    """
    params = list()
    conn = ut.create_connection(f_in)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT OperationID, Name, Type, Notes FROM t_operationparams where OperationID=?",(operation_id,))
        rows = cur.fetchall()
        for row in rows: 
            o = Parameter(row[0],row[1],row[2],row[3])
            params.append(o)
    return params