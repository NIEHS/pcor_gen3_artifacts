import logging
import unittest

from pcor_ingest.key_dataset_resource_parser import KeyDatasetResourceParser
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestKeyDatasetResourceParser(unittest.TestCase):

    def test_parse(self):
        test_ss_path = 'test_resources/key-datasets-sample.xlsx'
        actual = []
        parser = KeyDatasetResourceParser(pcor_testing_utilities.get_pcor_ingest_configuration())
        parser.parse(test_ss_path, actual)
        logger.info("parse_result: %s" % actual)
        self.assertIsNotNone(actual)


if __name__ == '__main__':
    unittest.main()