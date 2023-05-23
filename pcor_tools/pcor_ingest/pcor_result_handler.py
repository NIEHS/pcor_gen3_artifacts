import logging
import requests
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel
from pcor_ingest.pcor_reporter import PcorReporter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PcorResultHandler:
    """
    Handler results of pcor template ingest processing
    """

    def __init__(self, pcor_ingest_configuration):
        """
        Init
        :param pcor_ingest_configuration: PcorIngestConfiguration with config properties
        """
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.pcor_reporter = PcorReporter(pcor_ingest_configuration)

    def handle_result(self, pcor_process_result):
        """
        Handle the result of pcor template processing
        :param pcor_process_result: PcorProcessResult
        :return: void
        """

        logger.info("handle_result()")
        pcor_reporter = PcorReporter(self.pcor_ingest_configuration)
        pcor_reporter.report(pcor_process_result)

        # move files around TODO: add file processing to be handled in loader plugins