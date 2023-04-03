import os
import logging

ENV_CONFIG_LOCATION = 'PCOR_GEN3_CONFIG_LOCATION'

logger = logging.getLogger(__name__)


class PcorIngestConfiguration:
    """Configuration for ingesting data into PCOR catalog from some source"""

    def __init__(self, pcor_config_file_name):
        """
        initialize a config structure
        :param pcor_config_file_name: file path to pcor properties file
        """
        self.pcor_config_file_name = pcor_config_file_name
        self.pcor_props_dict = dict_from_props(self.pcor_config_file_name)
        self.gen3_creds_location = self.pcor_props_dict['gen3.creds.location']
        self.gen3_endpoint = self.pcor_props_dict['gen3.endpoint']


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


