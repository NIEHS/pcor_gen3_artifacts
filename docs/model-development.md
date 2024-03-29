# Model Development 

Docs for developing PCOR catalog model and encoding

## Intro    

The process for developing a catalog model for PCOR has the following workflow, (see each subsection in the workflow sequence for details):

1. Develop the abstract model, identifyig model nodes and properties within each node
2. Encode the model as .yaml using Gen3 syntax
3. Commit to Git and generate the schema in json format through an automated Git action or manually build schema using dump_schema.py
4. Bring up Gen3 with the new model for testing 
5. Encode the ETL transformations


## Develop the abstract model

The Abstract model for PCOR should follow a 'graph' pattern, where parent nodes point to child nodes representing different data types in a somewhat 
heirarchical structure. For example, an overall Program may contain various Projects. These Projects may consist of multiple studies and multiple publications.
The Studies may deal with a certain Event, such as a wildfire, and with certain Populations or Subjects.

As each node in the model, such as Subject and Event are defined, the specific properties, types, terms and other validation information need to be enumerated. 
This abstract metadata design as a graph of nodes and a specification of the properties in each node is then translated into the Gen3 YAML format

## Encode the model as .yaml

This repository is the canonical store for the .yaml files that encode the PCOR model. The yaml files are encoded in schemas section under schema/gdcdictionary/schemas.
Yaml is a markup language similar to JSON. 

* Here is reference documentation from Gen3 on [models](https://gen3.org/resources/user/dictionary/)
* Here is a [demonstration](https://gen3.datacommons.io/dd) of a data dictionary in Gen3


Each node in the model graph is represented in its own .yaml file as illustrated by this example. 

```yaml

$schema: "http://json-schema.org/draft-04/schema#"

id: "project"
title: Project
type: object
program: '*'
project: '*'
category: administrative
description: >
  Any specifically defined piece of work that is undertaken or attempted to meet a single
  requirement.
additionalProperties: false
submittable: true
validators: null

systemProperties:
  - id
  - state
  - released
  - releasable
  - intended_release_date

required:
  - code
  - name
  - dbgap_accession_number
  - programs

uniqueKeys:
  - [ id ]
  - [ code ]

links:
  - name: programs
    backref: projects
    label: member_of
    target_type: program
    multiplicity: many_to_one
    required: true

constraints: null

properties:
  type:
    type: string
  id:
    $ref: "_definitions.yaml#/UUID"
    systemAlias: node_id
    description: "UUID for the project." # TOREVIEW
  name:
    type: string
    description: "Display name/brief description for the project." # TOREVIEW
  code:
    type: string
    description: "Unique identifier for the project."
  investigator_name:
    description: "Name of the principal investigator for the project."
    type: string
  investigator_affiliation:
    description: "The investigator's affiliation with respect to a research institution."
    type: string
  date_collected:
    description: "The date or date range in which the project data was collected."
    type: string
  availability_type:
    description: "Is the project open or restricted?"
    enum:
      - Open
      - Restricted
  availability_mechanism:
    description: "Mechanism by which the project will be made avilable."
    type: string
  support_source:
    description: "The name of source providing support/grant resources."
    type: string
  support_id:
    description: "The ID of the source providing support/grant resources."
    type: string
  programs:
    $ref: "_definitions.yaml#/to_one"
    description: >
      Indicates that the project is logically part of the indicated project.
  state:
    description: |
      The possible states a project can be in.  All but `open` are
      equivalent to some type of locked state.
    default: open
    enum:
        # open: the only state users can perform 'upload' actions
        # possible actions in `open`:
        #   - upload (no state change)
        #   - review -> review
        #   - release (project.released -> true)
        - open

        # locked: admin has locked project for review
        # possible actions in `locked`:
        #   - open -> open
        #   - submit -> submitted
        #   - release (project.released -> true)
        - review

        # submitted: An admin has submitted project, it is locked against
        #            upload.
        # possible actions in `submitted`:
        #   - process -> processing
        #   - release (project.released -> true)
        - submitted

        # processing: The system is processing data in the project and
        #             is locked against upload and submission
        #   - (system transition to open)
        #   - release (project.released -> true)
        - processing


        # closed: The closed state is introduced to replace the
        #         ``legacy`` state and means that no further action
        #         can be taken on the project
        #   - (system transition to open)
        #   - release (project.released -> true)
        - closed

        # DEPRECATED(2016-03-01): synonymous with closed. included for
        #                         backwards compatibility
        - legacy

  released:
    description: |
      To release a project is to tell the GDC to include all submitted
      entities in the next GDC index.
    default: false
    type: boolean

  releasable:
    description: |
      A project can only be released by the user when `releasable` is true.
    default: false
    type: boolean

  intended_release_date:
    description: Tracks a Project's intended release date.
    type: string
    format: date-time
  dbgap_accession_number:
    type: string
    description: "The dbgap accession number provided for the project."

```

## Commit to Git to generate schema.json

The yaml files that describe Gen3 nodes need to be converted into a compact json format for reading by Gen3. The yaml files are read in by 
a [utility](../schema/dump_schema.py) that will emit the schema.json file. For our workflow, the act of committing changes to the model to 
GitHub will cause an action to run on GitHub that will run the schema tool and place the schema.json file in the custom_configs area of the repository at [schema.json](../custom_configs/schema.json).

The location on github is configured as the source of the schema information for Gen3, and Gen3 will load its schema from this location. Thus, a cycle of 
encoding in yaml, commit to GitHub, load in Gen3 is possible.

## Bring up Gen3 to view model

Gen3 will read the encoded schema.json and integrate model changes automatically. Here we focus on bringing up the model using a local
development workflow as described in the [local development workflow](./local-development-workflow.md) document. Please consult that doc for 
next steps.


## Encode the ETL Transformations

Data that is entered into Gen3 based on the encoded model is stored in a graph format serialized into a Postgres database. As data is entered, it goes through an ETL process 
to create the schema in Elasticsearch (OpenSearch) that is used by the Gen3 data portal. The ETL transformations are placed in the [custom_configs](../custom_configs/) in the [etlMapping.yaml](../custom_configs/etlMapping.yaml) file.

* [ETL Mapping Guide](https://github.com/uc-cdis/tube/blob/master/docs/configuration_file.md)
* [CDIS Model Repo] (https://github.com/uc-cdis/cdis-manifest)
