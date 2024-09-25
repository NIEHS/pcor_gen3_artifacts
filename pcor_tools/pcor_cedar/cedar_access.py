import logging
import requests
import json

from pcor_cedar.cedar_config import CedarConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

base_url = "https://resource.metadatacenter.org"
template_prefix = "https%3A%2F%2Frepo.metadatacenter.org%2Ftemplate-instances%2F"
test_instance_id1 = "53884d98-4425-4276-98f8-fef46bc6534d"

class CedarAccess(object):

    def __init__(self, cedar_file_name=None):
        self.cedar_file_name = cedar_file_name
        self.cedar_config = CedarConfig(cedar_file_name)




    def retrieve_chords_folder_contents(self):
        logger.info("retrieving chords folder contents")
        home_folder = self.cedar_config.cedar_properties["home_folder_id"]
        api_url = self.cedar_config.cedar_properties["cedar_endpoint"] + "/folders/" + home_folder
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.get(api_url, headers=headers)
        r_json = r.json()
        logger.debug("r:%s", r_json)
        return r_json


    def retrieve_resource(self, resource_id):

        """
        Retrieve the resource as a json-ld document
        Parameters
        ----------
        resource_id the GUID of the resource

        Returns
        -------
        JSON object that is the retrieved resource

        """
        logger.info("retrieving resource: %s" % resource_id)
        api_url = self.cedar_config.cedar_properties["cedar_endpoint"] + "/template-instances/" + template_prefix + resource_id
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.get(api_url, headers=headers)
        r_json = r.json()
        logger.debug("r:%s", r_json)
        return r_json
