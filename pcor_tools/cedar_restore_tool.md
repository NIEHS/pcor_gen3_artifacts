# CEDAR Loading Tool

## Intro    

The [CEDAR loading tool](./cedar_loading_tool.py) is a python script to load a CEDAR resource -or- bulk load
and entire CEDAR folder of resources into the CHORDS catalog (Gen3). The operator can navigate to a resource or 
directory URL on the CEDAR website, and copy that url into the command line for processing.

## Building

The pyinstaller [spec](./cedar_loading_tool.spec) is used to build the deployment via pyinstaller. 
[see](https://pyinstaller.org/en/stable/operating-mode.html#analysis-finding-the-files-your-program-needs)

Executing the command

```
 pyinstaller cedar_loading_tool.spec
```

Will create the distribution in [the dist folder](./dist/cedar_loading_tool)

## Configuration

Two configuration files are required

### Cedar Configuration

A cedar.properties file is required with the following form:

```properties
api_key=XXXXXX   # CEDAR API KEY
cedar_endpoint=https://resource.metadatacenter.org
# local working directory with processing, processed and failed subfolders
working_directory=/Users/conwaymc/temp/cedar 
# location of a measures rollup 
measures.location=/Users/conwaymc/Documents/workspace-pcor/pcor_gen3_artifacts/pcor_tools/tests/test_resources/MeasuresTermsv31.xlsx
```

This needs to configured as the environment variable: CEDAR_PROPERTIES

### CHORDS Configuration

A chords.properties file is required in the following form;

```properties
# location of a gen3 creds file that contains the tokens to access Gen3
gen3.creds.location=/Users/conwaymc/temp/test_resources/credentials.json
# location of the target Gen3
gen3.endpoint=https://staging.chords.nih
# information for email send of curator reports
smtp.server=smtp.niehs.nih.gov
mail.from=no-reply-pcor@niehs.nih.gov
mail.send_curator_email=True
# location of a measures rollup
measures.location=/Users/conwaymc/Documents/workspace-pcor/pcor_gen3_artifacts/custom_configs/MeasuresTermsv31.xlsx
# local working directory with processing, processed and failed subfolders
working.directory=/Users/conwaymc/Documents/scratch/pcor_work_dir

```

This needs to be configured as the environment variable: PCOR_GEN3_CONFIG_LOCATION

### Execution

Execute the loader as follows (to load a specific resource)

First, navigate in CEDAR to the desired resource and copy the URL, then issue:

```
./cedar_loading_tool -r 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/20215203-0960-4327-9b54-a79977511072?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F47ced533-508a-4b9e-a239-79e7dd819b2b'

```

This is an example of a single resource load, where -r is the URL to that resource. Depending on the
setting of the ```mail_send_curator_email``` flag in the cedar properties, a confirmation message 
will be sent via email.


