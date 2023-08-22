import PySimpleGUI as sg
import yaml
import persistence.packages as paks
import persistence.objects as objs
import persistence.operations as opers
import persistence.tags as tgs
from persistence.entities import Operation, OperationParameter, Object


conectors = list()  # list of entities.Connectors


def generate_paths(f_yaml: str, f_db: str, path_guid: str):
    """
    Generate  paths from the yaml file into the sparx model for the path guid
    Args:
        f_yaml (str): yaml file
        f_db (str): sparx ea db (.qea)
        path_guid (str): guid of the package in the sparx model where to generate the paths
    """
    with open(f_yaml, "r") as f:
        dict_spec = yaml.safe_load(f)

    if "paths" not in dict_spec.keys():
        sg.popup_error("paths do not exist in the specification")
        return

    dict_paths = dict_spec["paths"]

    # get root path package
    root_package = paks.get_package(f_db, path_guid)
    root_package_id = root_package.package_id

    for path_k, path_v in dict_paths.items():
        path_id = create_path(f_db, root_package_id, path_k, path_v)


def create_path(f_db: str, package_id: int, path_k: str, path_v: dict) -> int:
    """
    Creates an Interface object in the Sparx model with the Stereotype "Path"
    Args:
        f_db (str): sparx model db (.qea)
        package_id (int): package id where the object is generated
        path_k (str): the path uri
        path_v (dict): path content
    Returns:
        int: path object id
    """

    path_id = -1
    # determine path name
    split_path = path_k.split("/")
    if not split_path[-1].endswith("}"):
        path_name = split_path[-1]
    elif not split_path[-2].endswith("}"):
        path_name = split_path[-2]
    elif not split_path[-3].endswith("}"):
        path_name = split_path[-3]

    # invent a path name
    if split_path[-1].endswith("}") and path_name.endswith("s"):
        path_name = path_name[0:-1]
    path_name.capitalize()

    path_id = objs.create_object(f_db, package_id, "Interface", "Path", path_name)
    path_v["id"] = path_id

    # create tags
    tgs.create_tag(f_db, path_id, "path", path_k, None)

    # create operations for the path
    create_operations(f_db, path_id, path_k, path_v)
    return path_id


def create_operations(f_db: str, path_id: int, path_k: str, path_v: dict):
    """
    Create operations for the path object in the Sparx model
    Args:
        f_db (str): sparx model db (.qea)
        path_id (int): object id for which to create the operations
        path_k (str): path url
        path_v (dict): path content
    """

    if "get" in path_v.keys():
        create_get(f_db, path_id, path_k, path_v)
    if "post" in path_v.keys():
        create_post(f_db, path_id, path_k, path_v)
    if "put" in path_v.keys():
        create_put(f_db, path_id, path_k, path_v)
    if "patch" in path_v.keys():
        create_patch(f_db, path_id, path_k, path_v)
    if "delete" in path_v.keys():
        create_delete(f_db, path_id, path_k, path_v)


def create_get(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    ret_ref = {}
    ret_type = []
    ret_obj: Object
    ret_type_id = 0
    is_collection = "0"

    # create GET operation
    try:
        op_get = path_v["get"]
        r_200 = ""
        if "responses" in op_get.keys():
            dict_responses = op_get["responses"]
            if 200 in dict_responses.keys():
                r_200 = dict_responses[200]
            elif "200" in dict_responses.keys():
                r_200 = dict_responses["200"]
            if r_200 != "" and "application/json" in r_200["content"]:
                ret_ref = r_200["content"]["application/json"]["schema"]
                if "$ref" in ret_ref.keys():
                    # find operation type
                    ret_type = ret_ref["$ref"].split("/")
                    is_collection = "0"
                elif "type" in ret_ref.keys():
                    if ret_ref["type"] == "array":
                        # array of objects
                        if "$ref" in ret_ref["items"].keys():
                            ret_type = ret_ref["items"]["$ref"].split("/")
                        is_collection = "1"
                ret_obj = objs.get_object_by_name(f_db, ret_type[-1])
                if ret_obj is not None:
                    ret_type_id = ret_obj.object_id
                else:
                    ret_type_id = 0

                # create operation
                op = Operation(
                    0,
                    path_id,
                    "GET",
                    op_get["operationId"],
                    ret_type[-1],
                    is_collection,
                    ret_type_id,
                )
                op_id = opers.create_operation(f_db, op)
            else:
                op = Operation(0, path_id, "GET", op_get["operationId"], "binary", 0, 0)
                op_id = opers.create_operation(f_db, op)

            # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method get return {ret_ref}")
        raise (e)


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
    req_type = []
    req_obj: Object
    req_type_id = 0

    try:
        op_post = path_v["post"]
        # get the request body
        if "requestBody" in op_post.keys():
            req_body_type = op_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
            req_type = req_body_type.split("/")
            req_obj = objs.get_object_by_name(f_db, req_type[-1])
            if req_obj is None:
                req_type_id = 0
            else:
                req_type_id = req_obj.object_id

        # create operation
        op = Operation(0, path_id, "POST", op_post["operationId"], "int", 0, req_type_id)
        op_id = opers.create_operation(f_db, op)
        opPrm = OperationParameter(op_id, "request_body", req_type[-1], "in", 0, req_type_id)
        opers.create_operation_parameter(f_db, opPrm)

        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method post return {req_ref}")
        raise (e)


def create_put(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    req_ref = {}
    req_type = []
    req_obj: Object
    req_type_id = 0

    try:
        op_put = path_v["put"]
        # get the request body
        if "requestBody" in op_put.keys():
            req_body_type = op_put["requestBody"]["content"]["application/json"][
                "schema"
            ]["$ref"]
            req_type = req_body_type.split("/")
            req_obj = objs.get_object_by_name(f_db, req_type[-1])
            req_type_id = req_obj.object_id

        # create operation
        op = Operation(0, path_id, "PUT", op_put["operationId"], "int", 0, req_type_id)
        op_id = opers.create_operation(f_db, op)
        opPrm = OperationParameter(op_id, "request_body", req_type[-1], "in", 0, req_type_id)
        opers.create_operation_parameter(f_db, opPrm)

        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method post return {req_ref}")
        raise (e)


def create_patch(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    try:
        # create operation
        op_post = path_v["patch"]
        op = Operation(0, path_id, "PATCH", op_post["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)
        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method patch")
        raise (e)


def create_delete(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation

    try:
        # create operation
        op_del = path_v["delete"]
        op = Operation(0, path_id, "DELETE", op_del["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)

        # TODO add operation parametes

    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method delete")
        raise (e)
