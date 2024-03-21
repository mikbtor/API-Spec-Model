import type_generator as type_gen
import path_generator as path_gen


def generate_model(f_in: str, f_out: str, path_guid: str, type_guid: str):
    """_summary_

    Args:
        f_in (str): _description_
        f_out (str): _description_
        path_guid (str): _description_
        type_guid (str): _description_
    """    # generate types
    if(type_guid is not None and type_guid != ""):
        print("Generate Types")
        type_gen.generate_types(f_in, f_out, type_guid)
    if(path_guid is not None and path_guid != ""):
        print("Generate Paths")
        path_gen.generate_paths(f_in, f_out, path_guid, type_gen.types_package_id)
    print("Generation completed")

        



       