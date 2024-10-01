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

    def test_extract_guid(self):
        id = "https://repo.metadatacenter.org/template-element-instances/24102dc1-5116-407a-bc96-c344721cf198"
        expected = "24102dc1-5116-407a-bc96-c344721cf198"
        actual = LoaderCedar.extract_id_for_resource(id)
        self.assertEqual(expected, actual)