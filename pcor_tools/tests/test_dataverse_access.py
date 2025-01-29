import unittest
import logging
import json

from pcor_dataverse.dataverse_access import DataverseAccess

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

class TestDataverseAccess(unittest.TestCase):
    def test_basic_dataverse_search(self):
        dataverse_access = DataverseAccess('test_resources/dataverse_config_file.properties')
        search_params = {
            'q': '*',  # Query string
            'subtree': 'CAFE',  # Subtree filter
            'type': 'dataset'  # Specify dataset type
        }
        actual = dataverse_access.basic_dataverse_search(search_params)
        self.assertIsNotNone(actual)

    def test_get_dataset_metadata_by_persistent_id(self):
        dataverse_access = DataverseAccess('test_resources/dataverse_config_file.properties')
        persistent_id = 'doi:10.7910/DVN/QN92JF'
        actual = dataverse_access.get_dataset_metadata_by_persistent_id(persistent_id)
        self.assertIsNotNone(actual)

    def test_extract_doi_list_from_dataset_result(self):
        dataverse_access = DataverseAccess('test_resources/dataverse_config_file.properties')
        search_params = {
            'q': '*',  # Query string
            'subtree': 'CAFE',  # Subtree filter
            'type': 'dataset'  # Specify dataset type
        }
        query_result = dataverse_access.basic_dataverse_search(search_params)
        doi_list = dataverse_access.extract_doi_list_from_dataset_result(query_result)

        # Extract metadata for each doi and store it as a json file
        for doi in doi_list:
            persistent_id = doi
            dataset_metadata = dataverse_access.get_dataset_metadata_by_persistent_id(persistent_id)
            temp_dataset_id = dataset_metadata['data']['datasetId']
            logger.info('Dataset Metadata: %s', dataset_metadata)

            with open(f'test_resources/dataverse_dump/{temp_dataset_id}.json', 'w') as f:
                json.dump(dataset_metadata, f, indent=4)

        self.assertIsNotNone(doi_list)
