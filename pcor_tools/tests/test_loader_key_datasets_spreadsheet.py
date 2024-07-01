import logging
import unittest

from pcor_ingest.loader_key_datasets_spreadsheet import LoaderKeyDatasetsSpreadsheet

from tests import pcor_testing_utilities


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


class TestLoaderKeyDatasetsSpreadsheet(unittest.TestCase):

    def test_load(self):
        test_ss_path = 'test_resources/key-datasets-sample.xlsx'
        loader = LoaderKeyDatasetsSpreadsheet(pcor_testing_utilities.get_pcor_ingest_configuration())
        results = loader.process_load(test_ss_path)
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()
