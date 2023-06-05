import unittest
import logging

from pcor_ingest.loader import Loader
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


class TestLoaderSpreadsheet(unittest.TestCase):
    def test_process_test(self):
        pcor_ss_loader = Loader(pcor_ingest_configuration=pcor_testing_utilities.get_pcor_ingest_configuration())
        pcor_ss_loader.process_pcor_load(loader_type='spreadsheet',
                                         work_dir='/Users/pateldes/Documents/scratch/pcor_work_dir')


if __name__ == '__main__':
    unittest.main()
