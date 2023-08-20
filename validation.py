import re

def is_valid_input(f_in: str, f_out: str, path_guid: str, type_guid: str)->str:
    msg = ""
    if (f_in is None or f_in == ""):
        msg = "Please enter an input file \n"
    if (f_out is None or f_out == ""):
        msg += "Please enter a Sparx db output file\n"
    if (not  is_valid_guid(path_guid)):
        msg += "Path GUID format is incorrect\n"
    if (not is_valid_guid(type_guid)):
        msg += "Type GUID format is incorrect\n"
    return msg

def is_valid_guid(guid:str)->bool:
 
    # Regex to check valid
    # GUID (Globally Unique Identifier)
    regex = "^[{][0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]$"
         
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty return false
    if (guid == None):
        return False
 
    # Return if the string matched the ReGex
    if(re.search(p, guid)):
        return True
    else:
        return False