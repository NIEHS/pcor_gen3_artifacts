import json
import logging
import requests
from requests import HTTPError

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel
from pcor_ingest.pcor_template_process_result import PcorProcessResult

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
        :return: PcorProcessResult with the outcome
        """
        logger.info('Parsed_data %s ' % str(parsed_data))
        logger.info('Process()')
        model_data = parsed_data.model_data
        program_id = ''
        project_id = ''

        # ToDo: validate create response
        try:
            if 'program' in model_data.keys():
                logger.info('process:: adding program')
                program = model_data['program']
                try:
                    program_id = self.pcor_ingest.create_program(program=program)
                except HTTPError as pcor_error:
                    logger.error("error in submission:%s" % pcor_error)
                    submission_status = PcorProcessResult()
                    submission_status.success = False
                    submission_status.program_name = program
                    submission_status.request_content = pcor_error.request
                    submission_status.response_content = json.loads(pcor_error.response.text)
                    submission_status.path_url = submission_status.request_content.path_url
                    submission_status.program_name = program
                    logger.error("error in program create: %s" % submission_status)
                    return submission_status

                logger.info("program_id is: %s" % program_id)

                # program handled

                if 'project' in model_data.keys():
                    logger.info('process:: adding project')
                    project = model_data['project']
                    logger.info('Project %s' % str(project))

                    try:
                        project_id = self.pcor_ingest.create_project(program=program.name,
                                                        pcor_intermediate_project_model=project)
                    except HTTPError as pcor_error:
                        logger.error("error in submission:%s" % pcor_error)
                        submission_status = PcorProcessResult()
                        submission_status.success = False
                        submission_status.program_name = program
                        submission_status.project_id = project_id
                        submission_status.request_content = pcor_error.request
                        submission_status.response_content = json.loads(pcor_error.response.text)
                        submission_status.path_url = submission_status.request_content.path_url
                        submission_status.program_name = program
                        logger.error("error in project create: %s" % submission_status)
                        return submission_status

                    if 'resource' in model_data.keys():
                        logger.info('process:: adding resource')
                        resource = model_data['resource']
                        resource_submit_status = self.pcor_ingest.create_resource(
                            program_name=program.name,
                            project_name=project.name,
                            resource=resource)

                        # add a check if resource_submit_status.success == False
                        # if it fails, return the status and bail
                        if 'geospatial_data_resource' in model_data.keys():
                            logger.info('process:: adding geospatial_data_resource')
                            geo_spatial_resource = model_data['geospatial_data_resource']
                            geo_spatial_resource.resource_id = resource_submit_status.id
                            geo_spatial_resource.resource_submitter_id = resource.submitter_id
                            geo_spatial_resource.submitter_id = resource.submitter_id # FIXME: make submitter id a template field
                            resource_submit_status = self.pcor_ingest.create_geo_spatial_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_data_resource=geo_spatial_resource
                            )
                            # check status and bail if not success
                            if not resource_submit_status.success:
                                logger.error("creation of geospatial_data_resource failed, bailing: %s" % resource_submit_status)
                                return resource_submit_status

                        if 'pop_data_resource' in model_data.keys():
                            logger.info('process:: adding pop_data_resource')
                            pop_data_resource = model_data['pop_data_resource']
                            pop_data_resource.resource_id = resource_submit_status.id
                            pop_data_resource.resource_submitter_id = resource.submitter_id
                            pop_data_resource.submitter_id = resource.submitter_id # FIXME: make submitter id a template field

                            self.pcor_ingest.create_pop_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                pop_data_resource=pop_data_resource
                            )
                            if not resource_submit_status.success:
                                logger.error("creation of geospatial_data_resource failed, bailing: %s" % resource_submit_status)
                                return resource_submit_status

                        if 'geo_tool_resource' in model_data.keys():
                            logger.info('process:: adding geo_tool_resource')
                            geo_tool_resource = model_data['geo_tool_resource']
                            geo_tool_resource.resource_id = resource_submit_status.id
                            geo_tool_resource.resource_submitter_id = resource.submitter_id
                            geo_tool_resource.submitter_id = resource.submitter_id # FIXME: make submitter id a template field

                            self.pcor_ingest.create_geo_spatial_tool_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_tool_resource=geo_tool_resource
                            )
                            if not resource_submit_status.success:
                                logger.error("creation of geospatial_data_resource failed, bailing: %s" % resource_submit_status)
                                return resource_submit_status

                        # return status which will be success
                        return resource_submit_status

        except requests.HTTPError as exception:
            logger.error('Error occurred: %s' % str(exception))

# python3 run_spreadsheet /here/is/the/sheet.xls