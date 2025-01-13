import json
import unittest

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
from pcor_cedar.migration_key_dataset import CedarMigrateKeyDataset
from pcor_cedar.spreadsheet_to_cedar_migrate import SpreadsheetCedarMigrate
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from tests import pcor_testing_utilities


class TestSpreadsheetToCedarMigrate(unittest.TestCase):

    def test_migrate_key_datasets(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        target_file = 'test_resources/CHORDS-key-datasets-list_1.3-catalog-crosswalk.xlsx'
        cedar_configuration = CedarConfig()
        cedar_migrate = CedarMigrateKeyDataset(cedar_configuration, pcor_ingest_configuration)
        results = cedar_migrate.migrate(target_file)
        self.assertIsNotNone(results)


