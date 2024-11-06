import json
import unittest

from pcor_cedar.cedar_resource_reader import CedarResourceParser
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_resource_reader_150 import CedarResourceParser150
from tests import pcor_testing_utilities


class TestLoaderCedar(unittest.TestCase):

    def test_parse_geoexposure(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/geoexposure.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceParser()
        result = PcorProcessResult()
        reader.parse(json_file, result)
        self.assertTrue(result.success)

    def test_parse_population(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/population.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceParser()
        result = PcorProcessResult()
        reader.parse(json_file, result)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.model_data["population_data_resource"])


    def test_parse_geoexposure_tool(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/geoexposure_tool.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceParser()
        result = PcorProcessResult()
        reader.parse(json_file, result)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.model_data["geospatial_tool_resource"])

