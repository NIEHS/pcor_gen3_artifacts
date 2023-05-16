import logging
import json
import os
import pandas as pd


from pcor_ingest.gen3auth import PcorGen3Auth
from pcor_ingest.geospatial_data_resource_parser import GeoSpatialDataResourceParser
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, SubmitResponse, PcorDiscoveryMetadata, \
    Tag, AdvSearchFilter
from pcor_ingest.pcor_template_parser import PcorTemplateParseResult
from pcor_ingest.pcor_template_process_result import PcorTemplateProcessResult
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

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

    def __init__(self, pcor_ingest_configuration, gen3_auth=None, parsers={}, processors={},
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

        self.parsers["geospatial_data_resource"] = GeoSpatialDataResourceParser()

    def process_template_instance(self, template_absolute_path):
        """
        Process a single template instance, given the path to the spreadsheet file
        :param template_absolute_path: absolute path to the spreadsheet file
        :return: PcorActionResult object that indicates the success/failure and validation
        results
        """

        logger.info("process_template_instance for: %s" % template_absolute_path)
        type = self.determine_template_instance_type(template_absolute_path)
        logger.info("of type: %s" % type)

        parser = self.parsers[type]

        if parser is None:
            logger.error("No parser found for type: %s" % type)
            result = PcorTemplateParseResult()
            result.resource_type = type
            result.success = False
            result.source = template_absolute_path
            result.errors.append("no template parser found for type %s" % type)
            return result

        result = parser.parse(template_absolute_path)

        logger.info("result of parsing:%s" % result)

        # do the processing stuff here for a template

        # processer = processors[type] -> move to processing folder
        process_template = PcorTemplateProcessor()
        process_template.process(parsed_data=result)

        # result = processer.process

        # if result=success -> move to processed, notif, etc

        # if result=error -> send validation/error report

        pcor_action_result = PcorTemplateProcessResult()
        return pcor_action_result



    @staticmethod
    def determine_template_instance_type(template_absolute_path):
        """
        Determine the type (e.g. geospatial_data_resource) of an instance based on its contents
        :param template_absolute_path: absolute path to the template
        :return: string value which is the resource type, used for dictionary lookups
        """

        df = pd.read_excel(template_absolute_path, sheet_name=0)
        type_field = df.iat[2, 0]
        if type_field != "TYPE":
            logger.error("did not find expected TYPE field")
            raise "Cannot determine resource type via TYPE field"
        return df.iat[2, 1]