import json
import unittest

from pcor_cedar.cedar_loader_preprocessor import CedarLoaderPreprocessor
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from tests import pcor_testing_utilities


class TestCedarPreprocessor(unittest.TestCase):

    def test_preprocess_geoexposure(self):
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()
        json_file = 'test_resources/geoexposure.json'
        with open(json_file, 'r') as f:
            contents_json = json.loads(f.read())

        reader = CedarResourceReader_1_5_1()
        result = PcorProcessResult()
        reader.parse(json_file, result)

        preprocessor = CedarLoaderPreprocessor()

        preprocessor.process(result.model_data)
        self.assertIsNotNone(result.model_data)

