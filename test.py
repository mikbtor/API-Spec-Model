import yaml
import persistence.utils as db
from persistence import packages as p
from persistence import objects as ob
import re

def main():
    database = r"C:/Users/DrM/Documents/Architecture/Models/API Spec Generator/API Spec Generator.qea"
    regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"
    print(regex)
    guid = "{7E29D947-60C9-4741-A355-EBB2F7D18267"
    print (is_valid_guid(guid))



def is_valid_guid(guid:str)->bool:
    # Regex to check valid
    # GUID (Globally Unique Identifier)
    # regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"
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
    


if __name__ == '__main__':
    main()
