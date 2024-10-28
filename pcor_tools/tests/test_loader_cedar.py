import json
import unittest

from pcor_ingest.loader_cedar import LoaderCedar
from pcor_cedar.cedar_access import CedarAccess
from tests import pcor_testing_utilities


class TestLoaderCedar(unittest.TestCase):

    def test_load(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        loaderCedar = LoaderCedar(pcor_ingest_configuration)
        loaderCedar.process_load(pcor_ingest_configuration.working_directory)

    def test_load_individual_resource(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        loaderCedar = LoaderCedar(pcor_ingest_configuration)
        #url = "https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fc3e2f654-d6d1-402a-a64f-b3743a47fea2"

        # geo data
        #url = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/d4112c4b-def3-4770-974a-a564071d99e3?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fc3e2f654-d6d1-402a-a64f-b3743a47fea2'

        # pop data
        url = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/79d548ee-5b84-43e6-a8c0-1cdabed02e36?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fc3e2f654-d6d1-402a-a64f-b3743a47fea2'

        result = loaderCedar.process_individual_load(url)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)

    def test_extract_guid(self):
        id = "https://repo.metadatacenter.org/template-element-instances/24102dc1-5116-407a-bc96-c344721cf198"
        expected = "24102dc1-5116-407a-bc96-c344721cf198"
        actual = LoaderCedar.extract_id_for_resource(id)
        self.assertEqual(expected, actual)

    def test_extract_guid_from_resource_url(self):
        id = "https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/d4112c4b-def3-4770-974a-a564071d99e3?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fc3e2f654-d6d1-402a-a64f-b3743a47fea2"
        expected = "d4112c4b-def3-4770-974a-a564071d99e3"
        actual = LoaderCedar.extract_id_for_resource(id)
        self.assertEqual(expected, actual)