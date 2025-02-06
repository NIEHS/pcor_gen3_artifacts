import logging
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.loader_cedar import LoaderCedar
from pcor_ingest.ingest_context import PcorIngestConfiguration

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-r', "--resource_url", action='store', dest='resource_url', default=None)
    parser.add_option('-d', "--directory", action='store', dest='directory', default=None)
    parser.add_option('-v', "--cedar_version", action='store', dest='cedar_version', default="1_5_1")

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

    resource_url = args.resource_url
    directory = args.directory
    cedar_version = args.cedar_version

    pcor_ingest_configuration = PcorIngestConfiguration(os.environ.get("PCOR_GEN3_CONFIG_LOCATION"))
    cedar_loader = LoaderCedar(pcor_ingest_configuration, cedar_version)
    logger.info("loading...")
    cedar_loader.main_load_process(resource_url, directory)
    logger.info("loading complete")

if __name__ == "__main__":
    main()
