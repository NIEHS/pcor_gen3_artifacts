import json
import unittest

from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_resource_reader_pre_150 import CedarResourceParserPre150
from tests import pcor_testing_utilities


class TestLoaderCedar(unittest.TestCase):

    def test_parse(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/geoexposure.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceParserPre150()
        result = PcorProcessResult()
        reader.parse(json_file, result)
        self.assertTrue(result.success)
