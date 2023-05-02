import unittest
import json
import os
import logging
import pandas as pd


from unittest import TestCase
import requests

from pcor_ingest.geospatial_data_resource_parser import GeoSpatialDataResourceParser
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


class TestGeospatialDataRescourceParser(unittest.TestCase):

    def test_parse_program(self):
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        parser = GeoSpatialDataResourceParser()
        df = pd.read_excel(test_ss_path, sheet_name=0)
        actual = parser.extract_program_data(df)
        logger.info("program data: %s" % actual)
        self.assertIsNotNone(actual)


if __name__ == '__main__':
    unittest.main()
