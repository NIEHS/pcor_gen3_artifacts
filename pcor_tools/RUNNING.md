# Running PCOR Tools

## Setting up for testing

Unit tests are in the tests subdirectory. These depend on a local Gen3 (We use the Docker Compose version). 

### Download a credentials.json file

* Go to Gen3, log in, and select the 'Profile' page using the icon in the upper right.
* Select Create API key and download the file as credentials.json
* Place the credentials.json in the tests/test_resources subdirectory


### Setup properties 

* Add pcor.properties to pcor_ingest/tests/test_resources as per the example below


``` 

gen3.creds.location=/Users/conwaymc/Documents/workspace-pcor/pcor_gen3_artifacts/pcor_tools/tests/test_resources/credentials.json 
gen3.endpoint=https://localhost 

``` 

* Point pcor.properties to the abspath of the credentials as creds.location 

## create venv

Use Python 3.8+ 

### Set up Gen3

The Gen3 instance must be set up and running. It is important that the user has the ability to update
the catalog in Fence for the project and program. The user.yaml in custom_configs reflects the rights
necessary to run the tests.

### Notes and Tips

If you are running tests or running the code, and you get errors like:

```json
get_source    raise TemplateNotFound(template) from e
jinja2.exceptions.TemplateNotFound: project.jinja
```

This is probably due to your setup. Jinja uses a package loader, so you want to make sure your project is 
set up with pcor_tools as the root folder, with pcor_ingest as a python package under that root.


 