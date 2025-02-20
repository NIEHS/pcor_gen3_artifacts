import json
import unittest

from pcor_cedar.cedar_backup import CedarBackup
from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.loader_cedar import LoaderCedar
from pcor_cedar.cedar_access import CedarAccess

class TestCedarBackup(unittest.TestCase):
    def test_backup(self):
        cedar_configuration = CedarConfig()
        cedar_backup = CedarBackup()
        templates = cedar_configuration.cedar_properties['templates_folder']
        instances = cedar_configuration.cedar_properties['instances_folder']
        output = cedar_configuration.cedar_properties['working_directory']
        cedar_backup.backup(templates,instances, output)
        # add assertions check folder



