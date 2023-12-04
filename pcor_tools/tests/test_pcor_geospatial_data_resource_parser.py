import logging
import unittest

import pandas as pd

from pcor_ingest.geospatial_data_resource_parser import GeoSpatialDataResourceParser

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestGeospatialDataRescourceParser(unittest.TestCase):

    def test_parse_program(self):
        test_ss_path = '../pcor_ingest/spreadsheet/GeoExposure _template.xlsx'
        parser = GeoSpatialDataResourceParser()
        df = pd.read_excel(test_ss_path, sheet_name=0, engine='openpyxl')
        actual = parser.extract_program_data(df)
        logger.info("program data: %s" % actual)
        self.assertIsNotNone(actual)

    def test_parse_project(self):
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        parser = GeoSpatialDataResourceParser()
        df = pd.read_excel(test_ss_path, sheet_name=0, engine='openpyxl')
        actual = parser.extract_project_data(df)
        logger.info("project data: %s" % actual)
        self.assertIsNotNone(actual)

    def test_parse_details(self):
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        parser = GeoSpatialDataResourceParser()
        df = pd.read_excel(test_ss_path, sheet_name=0, engine='openpyxl')
        actual = parser.extract_resource_details(df)
        logger.info("resource details: %s" % actual)
        self.assertIsNotNone(actual)

    def test_parse_(self):
        test_ss_path = 'test_resources/pcor_geospatial_data_resource_test1.xlsx'
        parser = GeoSpatialDataResourceParser()
        actual = parser.parse(test_ss_path)
        logger.info("parse_result: %s" % actual)
        self.assertIsNotNone(actual)


if __name__ == '__main__':
    unittest.main()
