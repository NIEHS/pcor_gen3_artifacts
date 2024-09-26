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
