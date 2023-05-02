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
    def test_parse_for_type(self):
        ss_reader = PcorSpreadsheeetReader()


if __name__ == '__main__':
    unittest.main()
