import unittest

from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorTemplateProcessResult


class TestPcorReporter(unittest.TestCase):

    def test_render_template(self):
        pcor_processing_result = PcorTemplateProcessResult()
        pcor_reporter = PcorReporter()
        actual = pcor_reporter.produce_html_error_report(pcor_processing_result)
        self.assertIsNotNone(actual)

    def test_email_template(self):
        pcor_processing_result = PcorTemplateProcessResult()
        pcor_reporter = PcorReporter()
        report = pcor_reporter.produce_html_error_report(pcor_processing_result)
        pcor_reporter.send_email_report(report)


if __name__ == '__main__':
    unittest.main()
