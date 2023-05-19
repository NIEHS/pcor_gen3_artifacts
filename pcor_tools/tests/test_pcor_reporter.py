import json
import unittest

from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult
from tests import pcor_testing_utilities


class TestPcorReporter(unittest.TestCase):

    def test_format_error(self):
        pcor_processing_result = PcorProcessResult()
        pcor_reporter = PcorReporter(pcor_testing_utilities.get_pcor_ingest_configuration())
        f = open('test_resources/invalid_status1.json')

        data = json.load(f)
        pcor_processing_result.success = False
        pcor_processing_result.response_content = data

        report = pcor_reporter.produce_html_error_report(pcor_processing_result)
        pcor_reporter.send_email_report(pcor_processing_result, report)

    def test_format_success(self):
        pcor_processing_result = PcorProcessResult()
        pcor_reporter = PcorReporter(pcor_testing_utilities.get_pcor_ingest_configuration())

        f = open('test_resources/invalid_status1.json')

        data = json.load(f)
        pcor_processing_result.success = True
        pcor_processing_result.response_content = data

        report = pcor_reporter.produce_html_success_report(pcor_processing_result)
        pcor_reporter.send_email_report(pcor_processing_result, report)


if __name__ == '__main__':
    unittest.main()
