import logging
import json
import os

from pcor_ingest.gen3auth import PcorGen3Auth
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, SubmitResponse, PcorDiscoveryMetadata, \
    Tag, AdvSearchFilter

logger = logging.getLogger(__name__)


class PcorSpreadsheeetReader:
    """
    Represents the main reader of pcor spreadsheet templates, given a location,
    finds pcor templates and creates a parser appropriate to each template type. The
    reader than obtains a data structure from the parser and hands it off to a processor
    for that type. The processor then returns a result that goes to a result handler


    PcorSpreadSheetReader reads a template file and ->
    locates the PcorParser associated with that type ->
    PcorParser creates a set of PcorIntermediate models ->
    A PcorProcessor associated with that type is found and executed ->
    A PcorProcessingResult is returned ->
    A PcorProcessingResultHandler is invoked to handle the result of the action


    """

    def __init__(self, pcor_ingest_configuration, gen3_auth=None, parsers=[], processors=[],
                 result_handler=None):

        """
        Main initialization method for processing spreadsheets, takes a set of
        parsers, processors, result handler and dispatches to these components based on
        the type of template. The templates are parsed and processed and then a handler
        acts on the results of these actions

        :param pcor_ingest_configuration: IngestConfiguration with Gen3 server properties,
        processing properties
        :param gen3_auth: Optional Gen3Auth object if auth is done
        :param parsers: a dictionary of parser type and PcorSpreadsheetParser implementation
        :param processors: a dictionary of processor type and PcorSpreadsheetProcessor implementation
        :param result_handler: a PcorActionResultHandler implementation
        """

        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.parsers = parsers
        self.processors = processors
        self.result_handler = result_handler
        self.gen3_auth = gen3_auth

        if not gen3_auth:
            logger.info('doing auth')
            pcor_gen3_auth = PcorGen3Auth(pcor_ingest_configuration)
            self.gen3_auth = pcor_gen3_auth.authenticate_to_gen3()
            logger.info("authenticated to Gen3")

    def process_template_instance(self, template_absolute_path):
        """
        Process a single template instance, given the path to the spreadsheet file
        :param template_absolute_path: absolute path to the spreadsheet file
        :return: PcorActionResult object that indicates the success/failure and validation
        results
        """