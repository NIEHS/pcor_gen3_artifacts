import logging
import unittest
import os

from pcor_ingest.loader import Loader
from tests import pcor_testing_utilities
from tests import test_setup_scratch

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


class TestLoaderSpreadsheet(unittest.TestCase):
    def test_process_test(self):
        logger.info('this is a log from test!!!')
        scratch_dir = os.path.join(os.getcwd(), 'pcor_work_dir')
        test_setup_scratch.setup_scratch(path=scratch_dir)
        #pcor_ss_loader = Loader(pcor_ingest_configuration=pcor_testing_utilities.get_pcor_ingest_configuration())
        #pcor_ss_loader.process_pcor_load(loader_type='spreadsheet',
        #                                 work_dir='/Users/pateldes/Documents/scratch/pcor_work_dir')


if __name__ == '__main__':
    unittest.main()
