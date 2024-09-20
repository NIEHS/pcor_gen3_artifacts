import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


def dict_from_props(filename):
    """return a dictionary of properties file values"""
    logging.debug("dict_from_props()")
    logging.debug("filename: %s" % filename)

    my_props = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()  # removes trailing whitespace and '\n' chars

            if "=" not in line:
                continue  # skip blanks and comments w/o =
            if line.startswith("#"):
                continue  # skip comments which contain =

            k, v = line.split("=", 1)
            my_props[k] = v

    return my_props


class CedarConfig(object):

    """ init will load the cedar properties from the provided config file"""
    def __init__(self, config_file):
        self.config_file = config_file
        logger.info("loading config file from %s", config_file)
        self.cedar_properties = dict_from_props(config_file)
