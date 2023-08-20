import uuid
from dataclasses import dataclass, field

@dataclass
class Package:
    package_id:int
    parent_id:int
    ea_guid: str
    name:str

@dataclass
class Object:
    object_id: int
    package_id:int
    ea_guid:str    
    object_type:str
    stereotype:str
    name:str
    note:str = ""

@dataclass
class Enum:
    object_id: int
    package_id:int
    parent_id:int
    object_type:str    
    name:str
    note:str = ""

@dataclass
class Tag:
    property: str
    value:str

@dataclass
class Attribute:
    attribute_id: int
    name: str
    type:str

@dataclass
class Operation:
    operation_id:int
    object_id: int
    stereotype:str    
    name:str
    type:str
    return_array:int
    classifier: str
    ea_guid: str  = field(init=False)
    scope: str = "Public"
    note:str = ""
    
    def __post_init__(self):
        self.ea_guid = "{" + str(uuid.uuid1()) +"}"

@dataclass
class OperationParameter:
    operation_id:int
    name:str
    type:str
    kind:str    # (in, out)
    position:int     # display position
    classifier: int # the object_id if the type is an object, e.g. class
    ea_guid: str  = field(init=False)
    note:str = "" 

    def __post_init__(self):
        self.ea_guid = "{" + str(uuid.uuid1()) +"}"

@dataclass
class Connector:
    connector_id: int = field(init=False, default=0)
    ea_guid: str  = field(init=False)
    start_name: str
    start_obj_id: int 
    end_name: str
    end_obj_id: int = field(init=False, default=0)
    connector_type: str
    direction: str = field(init=False)
    dest_role: str
    dest_card: str 
    top_end_label: str
    bottom_end_label: str
    source_is_navigable: int = field(init=False)
    target_is_navigable: int = field(init=False)
    source_style: str = "Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Unspecified;"
    dest_style: str = "Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Navigable;"
    generalization_style: str = "Union=0;Derived=0;AllowDuplicates=0;"
    source_access:str = "Public"
    dest_access:str = "Public"

    def __post_init__(self):
        self.ea_guid = "{" + str(uuid.uuid1()) +"}"
        if self.connector_type == "Association":
            self.direction = "Source -> Destination"
            self.source_is_navigable = 0
            self.target_is_navigable = 1
        elif self.connector_type == "Generalization":
            self.direction = None
            self.source_is_navigable = 0
            self.target_is_navigable = 0
           
    

@dataclass
class ApiSpec:
    openapi: str = field(init=False)
    info: dict = field(init=False)
    tags: list = field(init=False)
    servers: list = field(init=False)
    paths: dict = field(init=False)
    components: dict = field(init=False)
    security: dict = field(init = False)

    def __post_init__(self):
        self.openapi = '3.0.2'
        self.info = { "version": '1.0', "title": "Open API Definition", "description": "API Definitions"}
        self.tags = []
        self.servers = [{"url":"http://localhost:8080", "description": "development server"}]
        self.paths = {}
        self.components = {"schemas":{}} 