# API-Spec-Model
Code to create objects in a Sparx EA model from an Open API specification. 
Still work in progress, does not cover all possible use cases. 
Imports both components/schemas and paths.
Specifics:
- allOf imported as inheritance
- $ref imported as associations

What is not implemented:
- referenced parameters
- not creating objects from referenced files
- anyOf not imported as it is not mapping directly to either inheritance or aggregation
  
