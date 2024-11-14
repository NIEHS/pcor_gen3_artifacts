"""
Tool to migrate a given cedar template from one version to another.

Requites an env variable "CEDAR_PROPERTIES" to be set. see ./tests/test_resources/cedar_config_file.properties
The env variable would be the absolute path to the location of that properties file
"""

import json
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_cedar.migration import CedarMigrate
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.loader_cedar import LoaderCedar

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

def setup_arguments():
    parser = OptionParser()
    parser.add_option('-r', "--resource_url", action='store', dest='resource_url', default=None)
    #parser.add_option('-f', "--working_file", action='store', dest='working_file', default=None)
    #parser.add_option('-t', "--cedar_target_url", action='store', dest='cedar_target_url', default=None)

    return parser.parse_args()[0]

def main():
    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    resource_url = args.resource_url # the resource to migrate, copied from the browser
    if not resource_url:
        logger.exception("no resource_url, specify this parameter with -r")
        raise Exception("no -r parameter specified")

    #working_file = args.working_file # scratch local working directory
    #cedar_target_url = args.cedar_target_url # location for migrated file
    cedar_config_file = os.environ.get("CEDAR_PROPERTIES")
    logger.info('resource to load :: %s' % resource_url)
    #logger.info('cedar target :: %s' % cedar_target_url)

    migrator = CedarMigrate(cedar_config_file)

    return migrator.migrate(resource_url)

if __name__ == "__main__":
    main()