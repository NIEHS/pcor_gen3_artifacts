import json
import unittest

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
from pcor_cedar.spreadsheet_to_cedar_migrate import CedarMigrate
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from tests import pcor_testing_utilities


class TestSpreadsheetToCedarMigrate(unittest.TestCase):

    def test_read_migrate_target(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        target_file = 'test_resources/GeoExposure_1.5.0 Center for Air, Climate, and Energy Solutions.xlsm'
        cedar_configuration = CedarConfig()
        cedar_migrate = CedarMigrate(cedar_configuration, pcor_ingest_configuration)
        result = cedar_migrate.read_migrate_target(target_file)

        self.assertTrue(result.success)

    def test_migrate_geoexposure(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        target_file = 'test_resources/GeoExposure_1.5.0 Center for Air, Climate, and Energy Solutions.xlsm'
        cedar_configuration = CedarConfig()
        cedar_migrate = CedarMigrate(cedar_configuration, pcor_ingest_configuration)
        name = cedar_migrate.migrate(target_file)
        self.assertIsNotNone(name)

    def test_migrate_population(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        target_file = 'test_resources/PopulationData_1.5.0 Health Care Cost Institute-2.xlsm'
        cedar_configuration = CedarConfig()
        cedar_migrate = CedarMigrate(cedar_configuration, pcor_ingest_configuration)
        name = cedar_migrate.migrate(target_file)
        self.assertIsNotNone(name)

    def test_migrate_geo_tool(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        target_file = 'test_resources/GeoExposureTool_1.5.0_EPA_Community_Multiscale_Air_Quality-CMAQ.xlsm'
        cedar_configuration = CedarConfig()
        cedar_migrate = CedarMigrate(cedar_configuration, pcor_ingest_configuration)
        name = cedar_migrate.migrate(target_file)
        self.assertIsNotNone(name)

