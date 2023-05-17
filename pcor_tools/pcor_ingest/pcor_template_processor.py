import logging
import uuid
import requests
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel

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

    def process(self, parsed_data):

        # example path /deep/documents/foo.xls
        # model data is dict [program=pcorIntermediateProgram,project= pcorIntermediateProject, resc, geospat resc]

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :return: PcorTemplateProcessResult with the outcome
        """
        logger.info('Parsed_data %s ' % str(parsed_data))
        logger.info('Process()')
        model_data = parsed_data.model_data

        # ToDo: validate create response
        try:
            if 'program' in model_data.keys():
                logger.info('process:: adding program')
                program = model_data['program']
                # ToDo: program dbgap_accession_number assignment logic?
                program.dbgap_accession_number = str(uuid.uuid4())
                self.pcor_ingest.create_program(program=program)

                if 'project' in model_data.keys():
                    logger.info('process:: adding project')
                    project = model_data['project']

                    # ToDo: project code and dbgap_accession_number assignment logic?
                    project.code = str(uuid.uuid4())
                    project.dbgap_accession_number = project.code

                    # ToDo: resolve following required fields getting 500 error when not present
                    project.complete = 'Complete'

                    logger.info('Project %s' % str(project))
                    self.pcor_ingest.create_project(program=program.name,
                                                    pcor_intermediate_project_model=project)

                    if 'resource' in model_data.keys():
                        logger.info('process:: adding resource')
                        resource = model_data['resource']
                        resource_submit_status = self.pcor_ingest.create_resource(
                            program_name=program.name,
                            project_name=project.name,
                            resource=resource)

                        if 'geo_spatial_resource' in model_data.keys():
                            logger.info('process:: adding geo_spatial_resource')
                            geo_spatial_resource = model_data['geo_spatial_resource']
                            geo_spatial_resource.resource_id = resource_submit_status.id
                            geo_spatial_resource.resource_submitter_id = resource.submitter_id
                            self.pcor_ingest.create_geo_spatial_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_data_resource=geo_spatial_resource
                            )

                        if 'pop_data_resource' in model_data.keys():
                            logger.info('process:: adding pop_data_resource')
                            pop_data_resource = model_data['pop_data_resource']
                            pop_data_resource.resource_id = resource_submit_status.id
                            pop_data_resource.resource_submitter_id = resource.submitter_id
                            self.pcor_ingest.create_pop_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                pop_data_resource=pop_data_resource
                            )

                        if 'geo_tool_resource' in model_data.keys():
                            logger.info('process:: adding geo_tool_resource')
                            geo_tool_resource = model_data['geo_tool_resource']
                            geo_tool_resource.resource_id = resource_submit_status.id
                            geo_tool_resource.resource_submitter_id = resource.submitter_id
                            self.pcor_ingest.create_geo_spatial_tool_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_tool_resource=geo_tool_resource
                            )

        except requests.HTTPError as exception:
            logger.error('Error occurred: %s' % str(exception))

