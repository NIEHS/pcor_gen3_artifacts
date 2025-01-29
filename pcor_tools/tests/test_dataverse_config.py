import unittest

from pcor_dataverse.dataverse_config import DataverseConfig


class TestDataverseConfig(unittest.TestCase):
    def test_dataverse_config(self):
        dataverse_config = DataverseConfig('test_resources/dataverse_config_file.properties')
        actual = dataverse_config.dataverse_properties
        self.assertIsNotNone(actual)
