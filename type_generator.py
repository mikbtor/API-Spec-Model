# pylint: disable=unused-argument, C0303, C0114,C0115,C0116, C0301, E1121, W0612, W0718, R0913, R0914, R1702, W0511, W0603, W1514

import traceback
import yaml
from persistence.entities import Connector
import persistence.packages as paks
import persistence.objects as objs
import persistence.tags as tgs
import persistence.attributes as atrs
import persistence.connectors as conns

conectors = [] # list of entities.Connectors
required = []
types_package_id: int = 0


basic_type_formats = {"int": {"type": "integer", "format": "int32"},
                      "float": {"type": "number", "format": "float"},
                      "double": {"type": "number", "format": "double"},
                      "numeric": {"type": "string"},
                      "date": {"type": "string", "format": "date"},
                      "time": {"type": "string", "format": "time"},
                      "datetime": {"type": "string", "format": "datetime"},
                      "boolean": {"type": "boolean"},
                      "string": {"type": "string"}}
rev_formats = {"int32":"integer",
               "int64":"integer",
               "float":"float",
               "double":"double",
               "date":"date",
               "time":"time",
               "datetime":"datetime"}

def generate_types(f_yaml: str, f_db:str,  type_guid: str) -> int:
    """
    Generate the resources defined in components/schemas
    Args:
        f_yaml (str): source yaml file
        f_db (str): Sparx EA *.qea file
        type_guid (str): Sparx EA GUID of the packages where Paths are to be generated
    """
    # global variables
    global required
    global types_package_id
    c:Connector
    o_id = 0
    is_req = 0

    try:
        with open(f_yaml, 'r') as f:
            dict_spec = yaml.safe_load(f)
    except FileNotFoundError as e:
        e.add_note(f"File {f_yaml} cannot be found")
        raise e
    
    try:
        dict_schemas = dict_spec["components"]["schemas"]
    except Exception as e:
        e.add_note("Components and schemas not defined in the file")
        raise e

    # get root path package
    root_types_pak = paks.get_package(f_db, type_guid)
    types_package_id = root_types_pak.package_id

    # create objects and attributes
    for k, ob in dict_schemas.items():
        try:
            if "required" in ob.keys():
                required = ob["required"]
            else:
                required = []

            if "allOf" in ob.keys():           
                # implement "allOf" as UML generalization, the source object being the child
                # create object
                o_id = objs.create_object(f_db, types_package_id, "Class", None, k)
                ob["id"] = o_id

                # create generalization connectors and attributes
                att_list = ob["allOf"]

                for att in att_list:
                    if "$ref" in att.keys():
                        dest_name = att["$ref"].split("/")
                        c = Connector(k, o_id, dest_name[-1] ,"Generalization", None, "1", None, "1")
                        conectors.append(c)
                    elif ("type" in att.keys()) and  (att["type"] == "object") and ("properties" in att.keys()):
                        try:
                            dict_as = att["properties"]
                            create_attributes(f_db, o_id, k, dict_as)
                        except Exception as e:
                            print(ob["title"])
                            print(dict_as)
                            traceback.print_exception(e)
                    
            elif "oneOf" in ob.keys():
                # TODO implement oneOf for objects
                print(f"Object {k} uses oneOf and is not imported")

            elif ("type" in ob.keys() and 'enum' in ob.keys()):
                # create enumeration
                o_id = objs.create_object(f_db, types_package_id, "Enumeration", None, k)
                ob["id"] = o_id

                #create attributes
                if "enum" in ob.keys():
                    list_enum = ob["enum"]
                    pos=0
                    for n in list_enum:
                        atrs.create_enum_attribute(f_db, o_id, n, pos)
                        pos +=1
            elif "type" in ob.keys():
                if  ob["type"] == "object":
                    # create object
                    o_id = objs.create_object(f_db, types_package_id, "Class", None, k)
                    ob["id"] = o_id
                    
                    #create attributes
                    if "properties" in ob.keys():
                        dict_atts = ob["properties"]
                        create_attributes(f_db, o_id, k, dict_atts) 
                else:
                    # this is an object of a basic type
                    
                    # create entities
                    o_id = objs.create_object(f_db, types_package_id, "Class", None, k)
                    ob["id"] = o_id
                    # create one attribute of that type
                    if k in required:
                        is_req=1
                    else:
                        is_req=0   
                    atrs.create_attribute(f_db, o_id, k.lower(), ob["type"], None, 0, is_req) 

            # create tags for required and discrimitator
            if "discriminator" in ob.keys():
                s_discriminator = ob["discriminator"]["propertyName"]
                tgs.create_obj_tag(f_db, o_id, "discriminator", s_discriminator, None)
            
            if "required" in ob.keys():
                l_required = ob["required"]
                s_required = str(l_required)
                if len(s_required)>100:
                    s_required = "Check specification"
                tgs.create_obj_tag(f_db, o_id, "required", str(s_required), None)                     
        except Exception as e:
            # do not raise, continue execution
            e.add_note(f"Exception raised when creating {k}")
            traceback.print_exception(e)

    # create connectors
    for c in conectors:
        try:
            o = objs.get_object_by_name(f_db, types_package_id, c.end_name)
            if o is not None:
                c.end_obj_id = o.object_id
                conns.create_connector(f_db,c)
            else:
                # create attribute
                if c.dest_role is None or c.dest_role == "":
                    c.dest_role = c.end_name.lower()
                atrs.create_attribute(f_db, c.start_obj_id, c.dest_role, c.end_name, None, 1,0)
        except Exception as e:
            # do not raise, continue execution
            e.add_note(f"Exception raised when creating connector {str(c)}")
            traceback.print_exception(e)
    return types_package_id


def create_attributes(f_db:str, o_id:int, source_name:str, dict_atts:dict):
       
    att_pos = 0
    att_id = 0
    att_type = ""
    is_req = 0

    for a_k, a_v in dict_atts.items():
        try:
            if a_k in required:
                is_req = 1
            else:
                is_req = 0
    
            if("type" in a_v.keys() and a_v["type"] != "array"):                
                if "format" in a_v.keys():
                    # formats are {int32, int64, float, double, date, time, datetime}
                    att_type = a_v["format"]
                    if "int32" == att_type or "int64" == att_type:
                        att_type = "integer"
                else:
                    att_type = a_v["type"]                                   
               
                att_id = atrs.create_attribute(f_db, o_id, a_k, att_type, att_pos, 0, is_req)
                att_pos =att_pos+1

                # create attribute tags 
                # assume the tag is a simple key:value tuple, where value is a string               
                for tg_k, tg_v in a_v.items():
                    if tg_k not in ["type", "format","description"] and len(str(tg_v))<100:
                        tgs.create_att_tag(f_db,att_id, tg_k, str(tg_v), None )
            elif("type" in a_v.keys() and a_v["type"] == "array"):
                # is it an array of objects? 
                if "type" in a_v["items"] and a_v["items"]["type"] != "object":
                    atrs.create_attribute(f_db, o_id, a_k, a_v["items"]["type"], att_pos, 1, is_req)
                    att_pos =att_pos+1
                elif "oneOf" in a_v["items"]:
                    # TODO implement oneOf for attributes
                    print("TODO implement oneOf for attributes")
                elif "allOf" in a_v["items"]:
                    # TODO implement allOf for attributes
                    print("TODO implement allOf for attributes")
                elif "$ref" in a_v["items"]:
                    dest_name = a_v["items"]["$ref"].split("/")[-1]
                    c = Connector(source_name, o_id, dest_name,"Association", a_k, "*", a_k, "*")
                    conectors.append(c)
            elif "$ref" in a_v.keys():
                dest_name = a_v["$ref"].split("/")[-1]
                c = Connector(source_name, o_id, dest_name,"Association", a_k, "1", a_k, "1")
                conectors.append(c)
        except Exception as e:
            # do not raise, continue execution
            e.add_note(f'Create attribute exception for:\n - object: {source_name}\n - attribute key: {a_k}\n attribute value: {a_v} \n')
            traceback.print_exception(e)
                   