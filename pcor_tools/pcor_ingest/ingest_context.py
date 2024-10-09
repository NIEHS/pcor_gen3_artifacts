import logging
import os

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
        self.smtp_server = self.pcor_props_dict['smtp.server']
        self.mail_from = self.pcor_props_dict['mail.from']
        self.measures_rollup = self.pcor_props_dict.get('measures.location')
        self.submitter_email = self.pcor_props_dict.get('submitter.email')
        self.working_directory = self.pcor_props_dict.get('working.directory')

        if not self.pcor_props_dict['mail.send_curator_email'] or str(self.pcor_props_dict['mail.send_curator_email']).lower() == 'no'  or str(self.pcor_props_dict['mail.send_curator_email']).lower() == 'false':
            self.mail_send_curator_email = False
        elif str(self.pcor_props_dict['mail.send_curator_email']).lower() == 'true' or str(self.pcor_props_dict['mail.send_curator_email']).lower() == 'yes':
            self.mail_send_curator_email = True

    @staticmethod
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

    @staticmethod
    def load_pcor_ingest_configuration_from_env():
        file_name = os.environ[ENV_CONFIG_LOCATION]
        if file_name is None:
            raise Exception("No PCOR_GEN3_CONFIG_LOCATION environment variable")
        return PcorIngestConfiguration(file_name)