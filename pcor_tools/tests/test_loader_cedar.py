import unittest

from pcor_cedar.loader_cedar import LoaderCedar
from tests import pcor_testing_utilities


class TestLoaderCedar(unittest.TestCase):

    def test_load(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        loaderCedar = LoaderCedar(pcor_ingest_configuration)
        loaderCedar.process_load_from_cedar_directory(pcor_ingest_configuration.working_directory)

    def test_load_individual_resource(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        loaderCedar = LoaderCedar(pcor_ingest_configuration=pcor_ingest_configuration, cedar_version='1_5_1')
        #url = "https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fc3e2f654-d6d1-402a-a64f-b3743a47fea2"

        # geo data
        #url = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/a683c649-6d2e-49bf-af39-bc39f39f14c2?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F47ced533-508a-4b9e-a239-79e7dd819b2b'

        # pop data
        #url = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/cc12b782-c07b-4ef9-9755-6556ff671473?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F47ced533-508a-4b9e-a239-79e7dd819b2b'

        # geo tool
        url = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/87f92251-8f16-4709-814b-bc567505f301?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2F47ced533-508a-4b9e-a239-79e7dd819b2b'

        result = loaderCedar.process_individual_load_of_cedar_resource_from_url(url)
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