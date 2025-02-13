import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_backup import CedarBackup

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-t', "--templates", action='store', dest='templates', default=None)
    parser.add_option('-i', "--instances", action='store', dest='instances', default=None)
    parser.add_option('-o', "--output", action='store', dest='output', default=None)

    return parser.parse_args()[0]


def main():
    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    templates = args.templates
    if not templates:
        logger.exception("no templates, specify this parameter with -t")
        raise Exception("no -t parameter specified")

    instances = args.instances

    if not instances:
        logger.error("no instances, specify this parameter with -i")
        raise Exception("no -i parameter specified")

    output = args.output

    if not output:
        logger.error("no output, specify this parameter with -o")
        raise Exception("no -o parameter specified")

    cedar_backup = CedarBackup()


if __name__ == "__main__":
    main()
