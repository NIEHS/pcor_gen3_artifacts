import logging
from unittest import TestCase
from pcor_ingest.ingest_context import parse_pcor_configuration

logger = logging.getLogger(__name__)

"""
refer properties.py for env variable and properties
"""


class Test(TestCase):

    def test_parse_pcor_configuration(self):
        result = parse_pcor_configuration('./pcor_test1.properties')
        self.assertIsNotNone(result)
        self.assertEqual('/cred/gen3.json', result.gen3_creds_file)



