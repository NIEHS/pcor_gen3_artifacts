"""
Tool to migrate spreadsheet format into CEDAR (for indiv types, not key dataset)

Requites an env variable "CEDAR_PROPERTIES" to be set. see ./tests/test_resources/cedar_config_file.properties
The env variable would be the absolute path to the location of that properties file

run parameters

-i - absolute path to the spreadsheet
-t - target version, e.g. 1_5_1

"""

import json
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_cedar.migration import CedarMigrate
from pcor_cedar.migration_key_dataset import CedarMigrateKeyDataset
from pcor_cedar.spreadsheet_to_cedar_migrate import SpreadsheetCedarMigrate
from pcor_ingest.ingest_context import PcorIngestConfiguration
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
    parser.add_option('-i', "--input_file", action='store', dest='input_file', default=None)
    parser.add_option('-t', "--target_version", action='store', dest='target_version', default=None)
    parser.add_option('-d', "--input_dir", action='store', dest='input_dir', default=None)
    return parser.parse_args()[0]

def main():

    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    if "PCOR_GEN3_CONFIG_LOCATION" not in os.environ:
        logger.error("PCOR_GEN3_CONFIG_LOCATION not found in env. System exiting...")
        sys.exit()

    cedar_config_file = os.environ.get("CEDAR_PROPERTIES")
    pcor_ingest_configuration = PcorIngestConfiguration(os.environ.get("PCOR_GEN3_CONFIG_LOCATION"))
    cedar_config = CedarConfig()

    migrator = SpreadsheetCedarMigrate(cedar_config, pcor_ingest_configuration)

    input_file = args.input_file
    input_dir = args.input_dir

    if input_file or input_dir:
        pass
    else:
        logger.exception("no input_file or input_dir provided, specify this parameter with -i for input file or -d for input dir")
        raise Exception("no -i or -d parameter specified")

    target_version = args.target_version

    if not target_version:
        logger.error("no target_version, specify this parameter with -t")
        raise Exception("no -t parameter specified")

    logger.info('input key datasets to load :: %s' % input_file)
    results = []
    migrator = SpreadsheetCedarMigrate(cedar_config, pcor_ingest_configuration)

    if input_file:
        logger.info("load individual file")
        results.append(migrator.migrate(input_file, target_version))
    else:
        results.extend(migrator.migrate_dir(input_dir, target_version))

if __name__ == "__main__":
    main()