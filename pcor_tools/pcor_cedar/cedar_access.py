import logging
import os
import urllib.parse
from logging import exception

import requests
import json

from jinja2 import Environment, FileSystemLoader

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
        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the relative path to your template directory
        template_rel_path = 'templates'

        # Construct the absolute path to the template directory
        template_dir = os.path.join(script_dir, template_rel_path)

        # Create a Jinja environment with the FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug('template_dir: %s' % template_dir)
        self.env.filters['jsonify'] = json.dumps

    def retrieve_chords_folder_contents(self):
        logger.info("retrieving chords folder contents")
        home_folder = self.cedar_config.cedar_properties["home_folder_id"]
        api_url = self.cedar_config.cedar_properties["cedar_endpoint"] + "/folders/" + home_folder
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.get(api_url, headers=headers)
        r_json = r.json()
        logger.debug("r:%s", r_json)
        return r_json

    def retrieve_loading_contents(self):
        logger.info("retrieving loading contents")

        loading_folder = self.cedar_config.cedar_properties["loading_folder_id"]
        api_url = self.cedar_config.cedar_properties["cedar_endpoint"] + "/folders/" + loading_folder + "/contents"
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.get(api_url, headers=headers)
        r_json = r.json()
        return self.parse_folder_listing(r_json)

    def create_resource(self, resource_json):
        logger.info("creating resource")
        cedar_folder = self.cedar_config.cedar_properties["cedar_folder"]
        api_url = self.cedar_config.cedar_properties["cedar_endpoint"] + "/template-instances?folder_id=" + cedar_folder
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.post(api_url, headers=headers, json=json.loads(resource_json))
        r_json = r.json()
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
        api_url = ("https://repo.metadatacenter.org/template-instances/" +
                   urllib.parse.quote_plus(resource_id))
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": self.cedar_config.build_request_headers_json()}
        r = requests.get(api_url, headers=headers)
        r_json = r.json()

        try:
            if r_json["statusCode"] is not 200:
                raise Exception(r_json["errorMessage"])
        except KeyError:
            pass

        logger.debug("r:%s", r_json)
        return r_json

    @staticmethod
    def parse_folder_listing(folder_listing_json):
        logger.info("parsing folder listing")
        folder = CedarFolder(folder_listing_json)
        return folder

    def produce_geoexposure_json(self, geoexposure_data):
        """
       Render discovery data as JSON via template
       :param discovery_data: PcorDiscoveryMetadata representing the resource data for discovery page
       :return: string with JSON for loading into Gen3
       """
        logger.info("produce_discovery_json()")
        template = self.env.get_template("cedar_geoexposure_resource.jinja")
        rendered = template.render(data=geoexposure_data)
        return rendered


class CedarFolder():

    def __init__(self, cedar_file_json = None, folder_name=None, folder_id=None, item_type = "folder"):
        if cedar_file_json:
            len_path_info = len(cedar_file_json["pathInfo"])
            if len_path_info > 0:
                self.folder_name = cedar_file_json["pathInfo"][len_path_info - 1]["schema:name"]
                self.folder_id = cedar_file_json["pathInfo"][len_path_info - 1]["@id"]
                self.item_type = "folder"
            else:
                raise Exception("No folder found")

            len_subfolders = len(cedar_file_json["resources"])
            if len_subfolders > 0:
                self.subfolders = []
                for subfolder in cedar_file_json["resources"]:
                    self.subfolders.append(CedarFolder(folder_name=subfolder["schema:name"],
                                                       folder_id=subfolder["@id"], item_type=subfolder["resourceType"]))
        else:
            self.folder_name = folder_name
            self.folder_id = folder_id
            self.item_type = item_type
            self.subfolders = []
