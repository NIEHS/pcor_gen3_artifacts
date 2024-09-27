import json
import unittest

from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_ingest.cedar_resource_reader import CedarResourceParser
from tests import pcor_testing_utilities


class TestLoaderCedar(unittest.TestCase):

    def test_parse(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/loading_contents.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceParser(pcor_ingest_configuration)
        result = PcorProcessResult()
        reader.parse(json_file, result)
        self.assertTrue(result.success)
