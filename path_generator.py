# pylint: disable=unused-argument, C0303, C0114,C0115,C0116, C0301, E1121, W0612, W0718, R0913, R0914, R1702, W0511, W0603, W1514

import traceback
import yaml
import PySimpleGUI as sg
import persistence.packages as paks
import persistence.objects as objs
import persistence.operations as opers
import persistence.tags as tgs
from type_generator import types_package_id as tp_id
from persistence.entities import Operation, OperationParameter, Object


conectors = []  # list of entities.Connectors
dict_req_bodies = {}
dict_parameters = {}
types_pckg_id: int = 0

def generate_paths(f_yaml: str, f_db: str, path_guid: str, types_package_id: int):
    """
    Generate  paths from the yaml file into the sparx model for the path guid
    Args:
        f_yaml (str): yaml file
        f_db (str): sparx ea db (.qea)
        path_guid (str): guid of the package in the sparx model where to generate the paths
    """
    global dict_req_bodies
    global dict_parameters
    global types_pckg_id

    types_pckg_id = types_package_id

    try:
        with open(f_yaml, "r") as f:
            dict_spec = yaml.safe_load(f)
    except Exception as e:
        e.add_note(f"Cannot access or convert the yaml file {f_yaml}")
        raise e
    
    if "paths" not in dict_spec.keys():
        sg.popup_error("paths do not exist in the specification")
        return

    dict_paths = dict_spec["paths"]

    # get root path package
    root_package = paks.get_package(f_db, path_guid)

    # get the request bodies
    if "components" in dict_spec.keys() and "requestBodies" in dict_spec["components"].keys():
        dict_req_bodies = dict_spec["components"]["requestBodies"]
    
    # get the parameters
    if "components" in dict_spec.keys() and "parameters" in dict_spec["components"].keys():
        dict_parameters = dict_spec["components"]["parameters"]

    if root_package is None:
        sg.popup_error("The path root package cannot be found; check the GUID value")
        return
    # root package id
    root_package_id = root_package.package_id

    # create paths
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
    path_name = "Undetermined"
    
    # determine path name, 
    # assume the format /root_resource/{resource_id}/sub_resource/{sub_resource_id}/....
    try:
        split_path = path_k.split("/")
        if split_path[-1].endswith("}"):
            #assuming the format {resource_id}
            path_name = split_path[-1][1:-4]
        else:
            path_name = split_path[-1]
        path_name.capitalize()

        path_id = objs.create_object(f_db, package_id, "Interface", None, path_name)
        path_v["id"] = path_id
    

        # create tags
        tgs.create_obj_tag(f_db, path_id, "path", path_k, None)

        # create operations for the path
        create_operations(f_db, path_id, path_k, path_v)
        return path_id
    except Exception as e:
        e.add_note(f"Path {path_name} cannot be created")
        traceback.print_exception(e)


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
        create_ppp_op(f_db, "post", path_id, path_k, path_v)
    if "put" in path_v.keys():
        create_ppp_op(f_db, "put", path_id, path_k, path_v)
    if "patch" in path_v.keys():
        create_ppp_op(f_db, "patch", path_id, path_k, path_v)
    if "delete" in path_v.keys():
        create_delete(f_db, path_id, path_k, path_v)


def create_get(f_db: str, path_id: int, path_k: str, path_v: dict):
    op: Operation
    ret_ref = {}
    ret_type = []
    ret_obj: Object
    ret_type_id = 0
    is_collection = "0"

    # global tp_id

    # create GET operation
    try:
        op_k = "get"
        op_v = path_v["get"]
        r_200 = ""
        if "responses" in op_v.keys():
            dict_responses = op_v["responses"]
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
                    ret_obj = objs.get_object_by_name(f_db, tp_id, ret_type[-1])
                    if ret_obj is not None:
                        ret_type_id = ret_obj.object_id
                    else:
                        ret_type_id = 0
                    # create operation that returns an object
                    op = Operation(0,path_id,"GET",op_v["operationId"],ret_type[-1],is_collection,ret_type_id)
                    op_id = opers.create_operation(f_db, op)
                elif "type" in ret_ref.keys():
                    if ret_ref["type"] == "array":
                        # array of objects
                        if "$ref" in ret_ref["items"].keys():
                            ret_type = ret_ref["items"]["$ref"].split("/")
                        is_collection = "1"
                        ret_obj = objs.get_object_by_name(f_db, tp_id, ret_type[-1])
                        if ret_obj is not None:
                            ret_type_id = ret_obj.object_id
                        else:
                            ret_type_id = 0
                        # create operation that returns an object
                        op = Operation(0,path_id,"GET",op_v["operationId"],ret_type[-1],is_collection,ret_type_id)
                        op_id = opers.create_operation(f_db, op)
                    else:
                        ret_type =ret_ref["type"]
                        op = Operation(0, path_id, "GET", op_v["operationId"], ret_type, 0, 0)
                        op_id = opers.create_operation(f_db, op)
            else:
                op = Operation(0, path_id, "GET", op_v["operationId"], "binary", 0, 0)
                op_id = opers.create_operation(f_db, op)

            # TODO operation parametes in query and path
            create_op_params(f_db, op_id, op_k, op_v)
    except Exception as e:
        e.add_note(f"Error processing path{path_k} and method get return {ret_ref}")
        traceback.print_exception(e)

def create_ppp_op(f_db: str, op_stype: str, path_id: int, path_k: str, path_v: dict):
    """
    Create an operation with the stereotype op_type for the object wtih the id = pth_id in t_object
    Args:
        f_db (str): db file name
        op_type: operation stereotype one of: [<<post>>, <<put>>, <<patch>>]
        path_id (int): object id
        path_k (str): path url
        path_v (dict): path dictionary

    Returns:
        _type_: n/a
    """

    # global dict_req_bodies
    # global types_pckg_id

    op: Operation
    req_types = []
    req_type = ""
    req_obj: Object
    req_type_id = 0

    try:
        op_k = op_stype
        op_v = path_v[op_stype]
        
        # create operation
        op = Operation(0, path_id, op_stype, op_v["operationId"], "int", 0, 0)
        op_id = opers.create_operation(f_db, op)

        # TODO add operation parametes

        # request body
        if "requestBody" in op_v.keys(): 
            if "content" in op_v["requestBody"].keys() and \
                    "application/json" in op_v["requestBody"]["content"].keys() and \
                        "schema" in  op_v["requestBody"]["content"]["application/json"].keys():
                if "$ref" in op_v["requestBody"]["content"]["application/json"]["schema"].keys():
                    req_body_type = op_v["requestBody"]["content"]["application/json"]["schema"]["$ref"]
                    req_types = req_body_type.split("/")
                    req_type=req_types[-1]
                    req_obj = objs.get_object_by_name(f_db, types_pckg_id, req_type)
                    if req_obj is None:
                        req_type_id = 0
                    else:
                        req_type_id = req_obj.object_id
                elif "type" in op_v["requestBody"]["content"]["application/json"]["schema"].keys():
                    req_type = op_v["requestBody"]["content"]["application/json"]["schema"]["type"]
                    req_type_id = 0
            elif "$ref" in op_v["requestBody"].keys():
                req_types = op_v["requestBody"]["$ref"].split("/")
                req_type = req_types[-1]
                req_obj = objs.get_object_by_name(f_db, types_pckg_id, req_type)
                if req_obj is None:
                    req_type_id = 0
                else:
                    req_type_id = req_obj.object_id
            
            # create operation parameter for the request body        
            op_prm = OperationParameter(op_id, "request_body", req_type, "in", 0, req_type_id)
            opers.create_operation_parameter(f_db, op_prm)

        # operation query and path parameters
        create_op_params(f_db, op_id, op_k, op_v)

    except Exception as e:
        e.add_note(f"Error creating operation {op_stype} for path{path_k}  with request body reference: {req_type}")
        traceback.print_exception(e)

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
        traceback.print_exception(e)
    
def create_op_params(f_db: str, op_id:int, op_k: str, op_v: dict):
    
    try:
        if "parameters" in op_v.keys():
            params = op_v["parameters"]
        
        # create operation parameters
        for param in params:
            p_name=""
            p_type = ""
            p_type_id = 0

            if isinstance(param,dict):
                p_name = param["name"]
                if "schema" in param.keys():
                    if "type" in param["schema"].keys():
                        if "format" in param["schema"].keys():
                            p_type = param["schema"]["format"]
                        else:
                            p_type =  param["schema"]["type"]
                        p_type_id = 0
                    elif "$ref" in param["schema"].keys():
                        p_type = param["schema"]["$ref"].split("/")[-1]
                        req_obj = objs.get_object_by_name(f_db, types_pckg_id, p_type)
                        if req_obj is None:
                            p_type_id = 0
                        else:
                            p_type_id = req_obj.object_id
                if "in" in param.keys() and "path" == param["in"] or "query"== param["in"]:
                    op_prm = OperationParameter(op_id, p_name, p_type, "in", 0, p_type_id)
                    opers.create_operation_parameter(f_db, op_prm)
            elif isinstance(param, list):
                for p in param:
                    # Get the definition of the parameter from the globa parametes dictionary
                    p_v = dict_parameters[p.split("/")[-1]]                   
                    # unpack the parameter
                    p_name = p_v["name"]
                    if "schema" in p_v.keys():
                        if "type" in p_v["schema"].keys():
                            if "format" in p_v["schema"].keys():
                                p_type = p_v["schema"]["format"]
                            else:
                                p_type =  p_v["schema"]["type"]
                            p_type_id = 0
                        elif "$ref" in p_v["schema"].keys():
                            p_type = p_v["schema"]["$ref"].split("/")[-1]
                            req_obj = objs.get_object_by_name(f_db, types_pckg_id, p_type)
                            if req_obj is None:
                                p_type_id = 0
                            else:
                                p_type_id = req_obj.object_id
                    if "in" in param.keys() and "path" == param["in"] or "query"== param["in"]:
                        op_prm = OperationParameter(op_id, p_name, p_type, "in", 0, p_type_id)
                        opers.create_operation_parameter(f_db, op_prm)
    except Exception as e:
        e.add_note(f"Error creating operation parameter for operation{op_k}")
        traceback.print_exception(e)
