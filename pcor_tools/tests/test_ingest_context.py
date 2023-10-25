import logging
from unittest import TestCase

from pcor_ingest.ingest_context import PcorIngestConfiguration

logger = logging.getLogger(__name__)

"""
refer properties.py for env variable and properties
"""


class Test(TestCase):

    def test_parse_pcor_configuration(self):
        result = PcorIngestConfiguration('../pcor_ingest/attic/pcor_test1.properties')
        self.assertIsNotNone(result)
        self.assertEqual('test_resources/credentials-local.json', result.gen3_creds_location)
        self.assertEqual('http://localhost:8080', result.gen3_endpoint)
