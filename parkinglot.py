import PySimpleGUI as sg
import yaml
import persistence.packages as paks
import persistence.objects as objs
import persistence.operations as opers
import persistence.tags as tgs
from persistence.entities import Operation, OperationParameter, Object

def create_post(f_db: str, path_id: int, path_k: str, path_v: dict):
    """
    Create an operation with the stereotype <<POST>> for the object wtih the id = pth_id in t_object
    Args:
        f_db (str): db file name
        path_id (int): object id
        path_k (str): path url
        path_v (dict): path dictionary

    Returns:
        _type_: n/a
    """
    op: Operation
    req_ref = {}
    req_types = []
    req_type = ""
    req_obj: Object
    req_type_id = 0

    try:
        op_post = path_v["post"]
        # get the request body
        if "requestBody" in op_post.keys() and \
                            "content" in op_post["requestBody"] and \
                                "application/json" in op_post["requestBody"]["content"].keys() and \
                                     "schema" in  op_post["requestBody"]["content"]["application/json"].keys():
            if "$ref" in op_post["requestBody"]["content"]["application/json"]["schema"].keys():
                req_body_type = op_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
                req_types = req_body_type.split("/")
                req_type=req_types[-1]
                req_obj = objs.get_object_by_name(f_db, req_type)
                if req_obj is None:
                    req_type_id = 0
                else:
                    req_type_id = req_obj.object_id
            elif "type" in op_post["requestBody"]["content"]["application/json"]["schema"].keys():
                req_type = op_post["requestBody"]["content"]["application/json"]["schema"]["type"]
                req_type_id = 0

        # create operation
        op = Operation(0, path_id, "POST", op_post["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)
        opPrm = OperationParameter(op_id, "request_body", req_type, "in", 0, req_type_id)
        opers.create_operation_parameter(f_db, opPrm)

        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method post return {req_ref}")
        raise (e)


def create_put(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    req_ref = {}
    req_types = []
    req_type = ""
    req_obj: Object
    req_type_id = 0

    try:
        op_put = path_v["put"]
        # get the request body
        if "requestBody" in op_put.keys():
            req_body_type = op_put["requestBody"]["content"]["application/json"]["schema"]["$ref"]
            req_types = req_body_type.split("/")
            req_type=req_types[-1]
            req_obj = objs.get_object_by_name(f_db, req_type)
            if req_obj is None:
                req_type_id=0
            else:
                req_type_id = req_obj.object_id

        # create operation
        op = Operation(0, path_id, "PUT", op_put["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)
        opPrm = OperationParameter(op_id, "request_body", req_type, "in", 0, req_type_id)
        opers.create_operation_parameter(f_db, opPrm)

        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method post return {req_ref}")
        raise (e)


def create_patch(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    op: Operation
    req_ref = {}
    req_types = []
    req_type = ""
    req_obj: Object
    req_type_id = 0

    try:
        # create operation
        op_patch= path_v["patch"]

        if "requestBody" in op_patch.keys():
            req_body_type = op_patch["requestBody"]["content"]["application/json"]["schema"]["$ref"]
            req_types = req_body_type.split("/")
            req_type=req_types[-1]
            req_obj = objs.get_object_by_name(f_db, req_type)
            if req_obj is None:
                req_type_id=0
            else:
                req_type_id = req_obj.object_id

        # create operation
        op = Operation(0, path_id, "PATCH", op_patch["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)

        # TODO add operation parametes
        opPrm = OperationParameter(op_id, "request_body", req_type, "in", 0, req_type_id)
        opers.create_operation_parameter(f_db, opPrm)

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method patch")
        raise (e)