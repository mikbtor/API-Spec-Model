from persistence.entities import Operation, OperationParameter
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
            o = OperationParameter(row[0],row[1],row[2],row[3])
            params.append(o)
    return params

def create_operation(f_db:str, op:Operation)->int:
    op_id = -1
    """
    Create an operation in the t_operation table
    :param f_db: Sparx DB file name
    :param op: Operation object
    :return: int
    """
    conn = ut.create_connection(f_db)
    sql = ''' INSERT INTO t_operation(Object_ID, ea_guid, Name, Stereotype, Scope, Type, Classifier, ReturnArray) VALUES(?,?,?,?,?,?,?,?) '''
        
    s_op = (op.object_id, op.ea_guid, op.name, op.stereotype, op.scope, op.type, op.classifier, op.return_array)
    
    with conn:
        cur = conn.cursor()
        cur.execute(sql, s_op)
        conn.commit()
    return cur.lastrowid

def create_operation_parameter(f_in: str, opPrm:OperationParameter) -> int:
    """
    Get the operations of an object with the given id from t_operations
    :param f_in: the database file name
    :param object_id: object id value
    :return:
    """
    conn = ut.create_connection(f_in)
    sql = ''' INSERT INTO t_operationparams(OperationID, ea_guid, Name, Type, Kind, Pos, Classifier) VALUES(?,?,?,?,?,?,?) '''
    sql_val = (opPrm.operation_id, opPrm.ea_guid, opPrm.name, opPrm.type, opPrm.kind, opPrm.position, opPrm.classifier)
    with conn:
        cur = conn.cursor()
        cur.execute(sql, sql_val)
        conn.commit()        
    return cur.lastrowid