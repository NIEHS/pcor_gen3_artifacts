"""
Tool to migrate a given cedar template from one version to another.

Requites an env variable "CEDAR_PROPERTIES" to be set. see ./tests/test_resources/cedar_config_file.properties
The env variable would be the absolute path to the location of that properties file

run parameters

-r - the url copied from CEDAR for the instance
-s - source version, e.g. 1_5_0
-t - target version, e.g. 1_5_1

restored = https://repo.metadatacenter.org/folders/f71236e0-fa24-42eb-bb98-a9bd8f6b2586

"""
import json
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.migration import CedarMigrate

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

def setup_arguments():
    parser = OptionParser()
    parser.add_option('-f', "--resource_file", action='store', dest='resource_file', default=None)
    parser.add_option('-t', "--target_folder_id", action='store', dest='target_folder_id', default=None)

    return parser.parse_args()[0]

def main():
    logger.info('Main function execution started. Load a backup json into CEDAR')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    cedar_config_file = os.environ.get("CEDAR_PROPERTIES")
    cedar_access = CedarAccess(cedar_config_file)

    resource_file = args.resource_file
    target_folder_id = args.target_folder_id

    if not resource_file:
        logger.error("no resource_file, specify this parameter with -f")
        raise Exception("no -s parameter specified")

    if not target_folder_id:
        logger.error("no target_folder_id, specify this parameter with -t")
        raise Exception("no -t parameter specified")

    cedar_config_file = os.environ.get("CEDAR_PROPERTIES")
    logger.info('resource to load :: %s' % resource_file)
    logger.info('target_folder_id :: %s' % target_folder_id)

    with open(resource_file, 'r') as f:
        contents_json = json.loads(f.read())

    id = cedar_access.create_resource(json.dumps(contents_json), target_folder_id)
    logger.info("complete..id: {id}".format(id=id))


if __name__ == "__main__":
    main()