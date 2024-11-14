import unittest

from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from pcor_cedar.migration import CedarMigrate
from tests import pcor_testing_utilities


class TestMigration150(unittest.TestCase):

    def test_read_migrate_target(self):
        migrate_source = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/d4112c4b-def3-4770-974a-a564071d99e3?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fa2fef183-d324-45d9-a9eb-beaf419d321c'
        migrator = CedarMigrate(None)
        resource = migrator.read_migrate_target(migrate_source)
        self.assertIsNotNone(resource)

    def test_reformat_json(self):
        migrate_source = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/d4112c4b-def3-4770-974a-a564071d99e3?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fa2fef183-d324-45d9-a9eb-beaf419d321c'
        migrator = CedarMigrate(None)
        resource = migrator.read_migrate_target(migrate_source)
        json_string = migrator.reformat_json(resource.model_data)
        self.assertIsNotNone(json_string)

    def test_migrate(self):
        migrate_source = 'https://cedar.metadatacenter.org/instances/edit/https://repo.metadatacenter.org/template-instances/d4112c4b-def3-4770-974a-a564071d99e3?folderId=https:%2F%2Frepo.metadatacenter.org%2Ffolders%2Fa2fef183-d324-45d9-a9eb-beaf419d321c'
        migrator = CedarMigrate(None)
        migrator.migrate(migrate_source)

