import requests
import logging

from pcor_dataverse.dataverse_config import DataverseConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class DataverseAccess:
    """
    Class to access the Dataverse repository
    """
    def __init__(self, dataverse_file_name=None):
        self.dataverse_file_name = dataverse_file_name
        self.dataverse_config = DataverseConfig(dataverse_file_name)

    def basic_dataverse_search(self, search_params):
        """
        Perform a basic search on the Dataverse repository
        """
        api_url = self.dataverse_config.dataverse_properties["dataverse_endpoint"] + "/api/search"
        api_headers = self.dataverse_config.build_request_headers_json()

        search_params['per_page'] = 500
        search_result = requests.get(api_url, headers=api_headers, params=search_params)
        if search_result.status_code == 200:
            search_result = search_result.json()
            logger.info('Data: %s', search_result)
            return search_result
        else:
            logger.info(f"Failed to retrieve data. Status code: {search_result.status_code}")

    def get_dataset_metadata_by_persistent_id(self, persistent_id):
        """
        Retrieve the metadata for a dataset by its persistent ID
        """
        api_url = (self.dataverse_config.dataverse_properties["dataverse_endpoint"] +
                   "/api/datasets/:persistentId/versions/:latest")
        api_headers = self.dataverse_config.build_request_headers_json()

        dataset_metadata = requests.get(api_url, headers=api_headers, params={'persistentId': persistent_id})
        if dataset_metadata.status_code == 200:
            dataset_metadata = dataset_metadata.json()
            logger.info('Data: %s', dataset_metadata)
            return dataset_metadata
        else:
            logger.info(f"Failed to retrieve data. Status code: {dataset_metadata.status_code}")

    @staticmethod
    def extract_doi_list_from_dataset_result(dataset_result):
        """
        Extract the DOIs from a dataset result
        """
        doi_list = []
        for dataset in dataset_result['data']['items']:
            doi_list.append(dataset['global_id'])
        return doi_list

