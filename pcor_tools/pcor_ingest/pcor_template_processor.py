import logging
import requests
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
        self.pcor_ingest = PcorGen3Ingest(PcorIngestConfiguration('test_resources/pcor.properties'))

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

        # ToDo: validate create response
        try:
            if 'program' in model_data.keys():
                logger.info('process:: adding program')
                self.pcor_ingest.create_program(program=model_data['program'])

                if 'project' in model_data.keys():
                    logger.info('process:: adding project')
                    self.pcor_ingest.create_project(program=model_data['program'].name,
                                                    pcor_intermediate_project_model=model_data['project'])

                    if 'resource' in model_data.keys():
                        logger.info('process:: adding resource')
                        resource_submit_status = self.pcor_ingest.create_resource(
                            program_name=model_data['program'].name,
                            project_name=model_data['project'].name,
                            resource=model_data['resource'])

                        if 'geo_spatial_resource' in model_data.keys():
                            logger.info('process:: adding geo_spatial_resource')
                            model_data['geo_spatial_resource'].resource_id = resource_submit_status.id
                            model_data['geo_spatial_resource'].resource_submitter_id = model_data['resource'].submitter_id
                            self.pcor_ingest.create_geo_spatial_data_resource(
                                program_name=model_data['program'].name,
                                project_name=model_data['project'].name,
                                geo_spatial_data_resource=model_data['geo_spatial_resource']
                            )

                        if 'pop_data_resource' in model_data.keys():
                            logger.info('process:: adding pop_data_resource')
                            model_data['pop_data_resource'].resource_id = resource_submit_status.id
                            model_data['pop_data_resource'].resource_submitter_id = model_data['resource'].submitter_id
                            self.pcor_ingest.create_pop_data_resource(
                                program_name=model_data['program'].name,
                                project_name=model_data['project'].name,
                                pop_data_resource=model_data['pop_data_resource']
                            )

                        if 'geo_tool_resource' in model_data.keys():
                            logger.info('process:: adding geo_tool_resource')
                            model_data['geo_tool_resource'].resource_id = resource_submit_status.id
                            model_data['geo_tool_resource'].resource_submitter_id = model_data['resource'].submitter_id
                            self.pcor_ingest.create_geo_spatial_tool_resource(
                                program_name=model_data['program'].name,
                                project_name=model_data['project'].name,
                                geo_spatial_tool_resource=model_data['geo_tool_resource']
                            )

        except requests.HTTPError as exception:
            logger.error('Error occurred: %s' % str(exception))

