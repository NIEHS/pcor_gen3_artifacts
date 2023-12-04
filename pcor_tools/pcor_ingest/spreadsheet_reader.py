import logging
import warnings
import pandas as pd
from pcor_ingest.gen3auth import PcorGen3Auth
from pcor_ingest.geospatial_data_resource_parser import GeoSpatialDataResourceParser
from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.population_data_resource_parser import PopulationDataResourceParser
from pcor_ingest.geospatial_tool_resource_parser import GeoSpatialToolResourceParser

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
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
        self.parsers["population_data_resource"] = PopulationDataResourceParser()
        self.parsers["geospatial_tool_resource"] = GeoSpatialToolResourceParser()
        self.result_handler = PcorReporter(pcor_ingest_configuration)

    def process_template_instance(self, template_absolute_path, result):
        """
        Process a single template instance, given the path to the spreadsheet file
        :param template_absolute_path: absolute path to the spreadsheet file
        :param result: PcorActionResult object that indicates the success/failure and validation
        results
        """

        logger.info("process_template_instance for: %s" % template_absolute_path)
        type = self.determine_template_instance_type(template_absolute_path)
        logger.info("of type: %s" % type)

        parser = self.parsers[type]

        if parser is None:
            logger.error("No parser found for type: %s" % type)
            result.resource_type = type
            result.success = False
            result.source = template_absolute_path
            result.errors.append("no template parser found for type %s" % type)
            return

        parser.parse(template_absolute_path, result)
        if not result.success:
            logger.error("error parsing: %s" % result)
            return
        else:
            logger.debug('parsing successful: %s' % result)
            return result

    @staticmethod
    def determine_template_instance_type(template_absolute_path):
        """
        Determine the type (e.g. geospatial_data_resource) of an instance based on its contents
        :param template_absolute_path: absolute path to the template
        :return: string value which is the resource type, used for dictionary lookups
        """
        warnings.simplefilter(action='ignore', category=UserWarning)
        df = pd.read_excel(template_absolute_path, sheet_name=0, engine='openpyxl')
        logger.info(df)
        type_field = df.iat[0, 0]
        val_field = df.iat[0, 1]
        logger.info("val:%s" % val_field)
        if type_field != "Type" or pd.isna(val_field):
            logger.error("did not find expected TYPE field")
            raise Exception("Cannot determine resource type via TYPE field")
        return df.iat[0, 1]
