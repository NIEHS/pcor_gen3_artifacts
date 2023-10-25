import logging
import unittest

from pcor_ingest.loader_spreadsheet import LoaderSpreadsheet

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


class TestLoaderSpreadsheet(unittest.TestCase):
    def test_add_timestamp(self):
        ss_orig = 'test1.xlsm'
        actual = LoaderSpreadsheet.add_timestamp_to_file(ss_orig)
        self.assertGreater(len(actual), len(ss_orig))

    def test_replace_timestamp(self):
        ss_orig = 'test1~pcor~_23_06_29_124427.xlsm'
        actual = LoaderSpreadsheet.add_timestamp_to_file(ss_orig)
        self.assertEqual(len(actual), len(ss_orig))


if __name__ == '__main__':
    unittest.main()
