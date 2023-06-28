import unittest

import json
import os
import logging

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.spreadsheet_reader import PcorSpreadsheeetReader
from tests import pcor_testing_utilities
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestSpreadsheetReader(unittest.TestCase):
    def test_determine_template_instance_type(self):
        ss_reader = PcorSpreadsheeetReader(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        actual = ss_reader.determine_template_instance_type(test_ss_path)
        self.assertEqual('geospatial_data_resource', actual)

    def test_process_template_instance(self):
        ss_reader = PcorSpreadsheeetReader(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_ss_path = 'test_resources/GeoExposure_1.3.0_EPA_AQS.xlsm'
        actual = ss_reader.process_template_instance(test_ss_path)


if __name__ == '__main__':
    unittest.main()
