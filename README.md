# API-Spec-Model
Code to create classes in a Sparx EA model from an Open API specification. 
Still work in progress, does not cover all possible use cases. 
Imports both components/schemas and paths.
Specifics:
- allOf imported as inheritance
- $ref imported as associations

What is not implemented:
- query and path parameters
- not creating objects from referenced files
- required not imported
- parameter qualifiers not imported
- anyOf not imported as it is not mapping directly to either inheritance or aggregation
  
