import json
import unittest

from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult
from tests import pcor_testing_utilities


class TestResultHandler(unittest.TestCase):

    def test_failure(self):
        pcor_processing_result = PcorProcessResult()
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()

        f = open('test_resources/invalid_status1.json')

        data = json.load(f)
        pcor_processing_result.success = False
        pcor_processing_result.response_content = data

        pcor_result_handler = PcorReporter(pcor_ingest_configuration)
        pcor_result_handler.report(pcor_processing_result)

    def test_success(self):
        pcor_processing_result = PcorProcessResult()
        pcor_ingest_configuration = pcor_testing_utilities.get_pcor_ingest_configuration()

        f = open('test_resources/invalid_status1.json')

        data = json.load(f)
        pcor_processing_result.success = True
        pcor_processing_result.response_content = data

        pcor_result_handler = PcorReporter(pcor_ingest_configuration)
        pcor_result_handler.report(pcor_processing_result)


if __name__ == '__main__':
    unittest.main()
