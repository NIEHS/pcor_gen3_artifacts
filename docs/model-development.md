# Model Development 

Docs for developing PCOR catalog model and encoding

## Intro    

The process for developing a catalog model for PCOR has the following workflow, (see each subsection in the workflow sequence for details):

1. Develop the abstract model, identifyig model nodes and properties within each node
2. Encode the model as .yaml using Gen3 syntax
3. Commit to Git and generate the schema in json format through an automated Git action or manually build schema using dump_schema.py
4. Bring up Gen3 with the new model for testing 


## Develop the abstract model



