import os
import logging

ENV_CONFIG_LOCATION = 'PCOR_GEN3_CONFIG_LOCATION'

logger = logging.getLogger(__name__)


class PcorIngestConfiguration:
    """Configuration for ingesting data into PCOR catalog from some source"""

    def __init__(self, pcor_config_file_name, gen3_creds_file, gen3_endpoint):
        """
        initialize a config structure
        :param pcor_config_file_name: file path to pcor properties file
        :param gen3_creds_file: path to gen3 configs file
        :param gen3_endpoint: address of Gen3
        """
        self.pcor_config_file_name = pcor_config_file_name
        self.gen3_creds_file = gen3_creds_file
        self.gen3_endpoint = gen3_endpoint


def parse_pcor_configuration(pcor_config_location):
    """
    From a file path that points to a pcor.properties file, return the configuration
    :param pcor_config_location: location of the pcor config
    :return: pcor_configuration
    """

    pcor_props_dict = dict_from_props(pcor_config_location)
    gen3_location = pcor_props_dict['gen3.creds.location']
    pcor_ingest_configuration = PcorIngestConfiguration(pcor_config_location, gen3_location)
    return pcor_ingest_configuration


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


