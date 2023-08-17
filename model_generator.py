import yaml
from persistence.entities import Package, Object, Connector
import persistence.packages as paks
import persistence.objects as objs
import persistence.attributes as atrs
import persistence.connectors as conns

conectors = list() # list of entities.Connectors


def generate_model(f_in: str, f_out: str, path_guid: str, type_guid: str):
    generate_api_model(f_in, f_out, path_guid, type_guid)


def generate_api_model(f_yaml: str, f_db:str, path_guid: str, type_guid: str):
    
    global conectors
    c:Connector

    with open(f_yaml, 'r') as f:
        dict_spec = yaml.safe_load(f)
    
    dict_schemas = dict_spec["components"]["schemas"]
    
    # get root path package
    root_types_pak = paks.get_package(f_db, type_guid)
    package_id = root_types_pak.package_id
    
    # create objects and attributes
    for k, ob in dict_schemas.items():
        #TO DO need to take into account 'oneOf' as well
        if "type" in ob.keys() and ob["type"] == "object":
            if "allOf" not in ob.keys() and "oneOf" not in ob.keys():
                # create entities
                o_id = objs.create_object(f_db, package_id, "Class", None, k)
                ob["id"] = o_id
                
                #create attributes
                if "properties" in ob.keys():
                    dict_atts = ob["properties"]
                    create_attributes(f_db, o_id, k, dict_atts) 
                
                # create tags for required and discrimitator
                      
            elif "allOf" in ob.keys():           
                #create object
                o_id = objs.create_object(f_db, package_id, "Class", None, k)
                ob["id"] = o_id

                #create generalization connectors and attributes
                att_list = ob["allOf"]

                for att in att_list:
                    if( "$ref" in att.keys()):
                        dest_name = att["$ref"].split("/")
                        c = Connector(k, o_id, dest_name[-1] ,"Generalization", None, "1", None, "1")
                        conectors.append(c)
                    elif("type" in att.keys() and  (att["type"] == "object")):
                        try:
                            dict_as = att["properties"]
                            create_attributes(f_db, o_id, k, dict_as)
                        except Exception as e:
                            print(e)
                            print(ob["title"])
                            print(dict_as)

                # create tags for required and discrimitator  
            elif "oneOf" in ob.keys():
                print("TODO implement oneOf for objects")                          
        elif ("type" in ob.keys() and 'enum' in ob.keys()):
            # create enumeration
            o_id = objs.create_object(f_db, package_id, "Enumeration", None, k)
            ob["id"] = o_id

            #create attributes
            if "enum" in ob.keys():
                list_enum = ob["enum"]
                pos=0
                for n in list_enum:
                    atrs.create_enum_attribute(f_db, o_id, n, pos)
                    pos +=1
    # create connectors
    for c in conectors:
        o = objs.get_object_by_name(f_db, c.end_name)
        if o is not None:
            c.end_obj_id = o.object_id
            conns.create_connector(f_db,c)
        else:
            # create attribute
            if c.dest_role is None or c.dest_role == "":
                c.dest_role = c.end_name.lower()
            
            atrs.create_attribute(f_db, c.start_obj_id, c.dest_role, c.end_name, None, 1)



def create_attributes(f_db:str, o_id:int, source_name:str, dict_atts:dict):
    
    global connectors
    
    att_pos = 0
    for a_k, a_v in dict_atts.items():
        if("type" in a_v.keys() and a_v["type"] != "array"):
            atrs.create_attribute(f_db, o_id, a_k, a_v["type"], att_pos, 0)
            att_pos =att_pos+1
        elif("type" in a_v.keys() and a_v["type"] == "array"):
            # is it an array of objects? 
            if "type" in a_v["items"] and a_v["items"]["type"] != "object":
                atrs.create_attribute(f_db, o_id, a_k, a_v["items"]["type"], att_pos, 1)
                att_pos =att_pos+1
            elif "oneOf" in a_v["items"]:
                print("TODO implement oneOf for attributes")
            elif "allOf" in a_v["items"]:
                print("TODO implement allOf for attributes")
            else:
                dest_name = a_v["items"]["$ref"].split("/")
                c = Connector(source_name, o_id, dest_name[-1],"Association", a_k, "*", a_k, "*")
                conectors.append(c)
        elif ("$ref" in a_v.keys()):
            dest_name = a_v["$ref"].split("/")
            c = Connector(source_name, o_id, dest_name[-1],"Association", a_k, "1", a_k, "1")
            conectors.append(c)



       