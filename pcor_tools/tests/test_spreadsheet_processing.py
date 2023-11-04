import logging
import os
import unittest

from pcor_ingest.pcor_template_process_result import PcorProcessResult
from pcor_ingest.spreadsheet_reader import PcorSpreadsheeetReader
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestSpreadsheetProcessing(unittest.TestCase):
    def test_determine_template_instance_type(self):
        ss_reader = PcorSpreadsheeetReader(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        actual = ss_reader.determine_template_instance_type(test_ss_path)
        self.assertEqual('geospatial_data_resource', actual)

    def test_process_template_instance(self):
        logger.info('starting test_process_template_instance process')
        ss_reader = PcorSpreadsheeetReader(pcor_testing_utilities.get_pcor_ingest_configuration())
        result = PcorProcessResult()

        ss_list = [
            'test_resources/GeoExposure_1.3.0_EPA_AQS.xlsm',
            'test_resources/GeoExposure_1.3.0_MTBS.xlsm',
            'test_resources/GeoExposure_1.3.0_NASA_MODIS.xlsm',
            'test_resources/GeoExposure_1.3.0_Vargo_Smoke.xlsm'
        ]

        for test_ss_path in ss_list:
            logger.info('starting loading process')
            result.template_source = os.path.join(os.getcwd(), test_ss_path)
            actual = ss_reader.process_template_instance(test_ss_path, result)


if __name__ == '__main__':
    unittest.main()
