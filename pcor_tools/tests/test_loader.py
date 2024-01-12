import logging
import unittest
import os
import shutil

from pcor_ingest.loader import Loader
from tests import pcor_testing_utilities
from tests import test_setup_scratch

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


class TestLoaderSpreadsheet(unittest.TestCase):

    def test_single_SS_load(self):
        """
        will copy one SS in test_resources folder to scratch work dir and load to gen3
        """
        logger.info('test_single_SS_load()')

        # Create scratch folder under tests ( .gitignore updated )
        # scratch_dir location can be changed as per preference

        #scratch_dir = os.path.join(os.getcwd(), 'pcor_work_dir')
        scratch_dir = '/Users/pateldes/Documents/scratch/pcor_work_dir'
        test_setup_scratch.setup_scratch(path=scratch_dir)

        # copy SS from test resources to new folder
        new_folder = os.path.join(scratch_dir, 'new')
        test_resources = os.path.join(os.getcwd(), 'test_resources')

        file_name = 'GeoExposure_1.3.0_EPA_AQS.xlsm'
        shutil.copy(os.path.join(test_resources, file_name), new_folder)

        # init loader obj
        pcor_ss_loader = Loader(pcor_ingest_configuration=pcor_testing_utilities.get_pcor_ingest_configuration())
        pcor_ss_loader.process_pcor_load(loader_type='spreadsheet', file_path=os.path.join(new_folder, file_name))

    def test_bulk_SS_load(self):
        """
        will copy all SS in test_resources folder to scratch work dir and load to gen3
        """
        logger.info('test_bulk_SS_load()')

        # Create scratch folder under tests ( .gitignore updated )
        # scratch_dir location can be changed as per preference

        scratch_dir = os.path.join(os.getcwd(), 'pcor_work_dir')
        test_setup_scratch.setup_scratch(path=scratch_dir)

        # copy all SS from test resources to new folder
        new_folder = os.path.join(scratch_dir, 'new')
        test_resources = os.path.join(os.getcwd(), 'test_resources')

        files = os.listdir(test_resources)
        for file in files:
            if file.endswith(".xlsm"):
                shutil.copy(os.path.join(test_resources, file), new_folder)

        # init loader obj
        pcor_ss_loader = Loader(pcor_ingest_configuration=pcor_testing_utilities.get_pcor_ingest_configuration())

        # load all the test SS in new folder
        test_files = os.listdir(new_folder)
        if len(test_files) > 0:
            for test_file in test_files:
                pcor_ss_loader.process_pcor_load(loader_type='spreadsheet', file_path=os.path.join(new_folder, test_file))


if __name__ == '__main__':
    unittest.main()
