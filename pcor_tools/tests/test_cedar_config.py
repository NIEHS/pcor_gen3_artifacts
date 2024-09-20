from _pytest import unittest

from pcor_cedar.cedar_config import CedarConfig
import logging
import unittest
import os
import shutil

from pcor_ingest.loader import Loader
from tests import pcor_testing_utilities
from tests import test_setup_scratch

class TestCedarConfig(unittest.TestCase):
    def test_cedar_config(self):
        cedar_config = CedarConfig('test_resources/cedar_config_file.properties')
        actual = cedar_config.cedar_properties
        self.assertIsNotNone(actual)

