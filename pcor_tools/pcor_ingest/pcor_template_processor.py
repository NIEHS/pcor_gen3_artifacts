import logging
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.ingest_context import PcorIngestConfiguration

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PcorTemplateProcessor:
    """
    A parent class for a processor of a PCOR spreadsheet template for a type
    """

    def __init__(self):
        pass

    def process(self, template_absolute_path, model_data):

        # example path /deep/documents/foo.xls
        # model data is dict [program=pcorIntermediateProgram,project= pcorIntermediateProject, resc, geospat resc]

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :return: PcorTemplateProcessResult with the outcome
        """
        logger.info('Process()')
        logger.info('Template absolute path %s' % template_absolute_path)
        logger.info('Model data %s' % str(model_data))

        if 'program' in model_data.keys():
            pcor_ingest = PcorGen3Ingest(PcorIngestConfiguration('test_resources/pcor.properties'))
            pcor_ingest.create_program(program=model_data['program'])

