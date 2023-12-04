import json
import logging
import traceback
import requests
from requests import HTTPError
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, AdvSearchFilter

from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PcorTemplateProcessor:
    """
    A parent class for a processor of a PCOR spreadsheet template for a type
    """

    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest = PcorGen3Ingest(pcor_ingest_configuration)

    def process(self, parsed_data):

        # example path /deep/documents/foo.xls
        # model data is dict [program=pcorIntermediateProgram,project= pcorIntermediateProject, resc, geospat resc]

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param parsed_data: PcorProcessResult with the parsed data included
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
                parsed_data.program_name = program.name
                try:
                    program_id = self.pcor_ingest.create_program(program=program)
                except HTTPError as pcor_error:
                    logger.error("error in submission:%s" % pcor_error)
                    parsed_data.success = False
                    parsed_data.request_content = pcor_error.request
                    parsed_data.response_content = json.loads(pcor_error.response.text)
                    parsed_data.path_url = parsed_data.request_content.path_url
                    logger.error("error in program create: %s" % parsed_data)
                    return

                logger.info("program_id is: %s" % program_id)

                # program handled

                if 'project' in model_data.keys():
                    logger.info('process:: adding project')
                    project = model_data['project']
                    logger.info('Project %s' % str(project))

                    try:
                        project_id = self.pcor_ingest.create_project(program=program.name,
                                                                     pcor_intermediate_project_model=project)
                        parsed_data.project_id = project_id

                    except HTTPError as pcor_error:
                        logger.error("error in submission:%s" % pcor_error)
                        parsed_data.success = False
                        parsed_data.request_content = pcor_error.request
                        parsed_data.response_content = json.loads(pcor_error.response.text)
                        parsed_data.path_url = parsed_data.request_content.path_url
                        parsed_data.message = pcor_error.response.text
                        parsed_data.traceback = traceback.format_exc(pcor_error)
                        logger.error("error in project create: %s" % pcor_error)
                        return

                    if 'resource' in model_data.keys():
                        logger.info('process:: adding resource')
                        resource = model_data['resource']
                        resource_submit_status = self.pcor_ingest.create_resource(
                            program_name=program.name,
                            project_code=project.name,
                            resource=resource)

                        # add a check if resource_submit_status.success == False

                        if not resource_submit_status.success:
                            logger.error(
                                "creation of resource failed, bailing: %s" % resource_submit_status)
                            parsed_data.success = False
                            parsed_data.message = resource_submit_status.message
                            parsed_data.errors += resource_submit_status.errors
                            parsed_data.path_url = resource_submit_status.path_url
                            parsed_data.response_content = resource_submit_status.response_content
                            parsed_data.request_content = resource_submit_status.request_content
                            return

                        # if it fails, return the status and bail

                        if 'geospatial_data_resource' in model_data.keys():
                            logger.info('process:: adding geospatial_data_resource')
                            geo_spatial_resource = model_data['geospatial_data_resource']
                            geo_spatial_resource.resource_id = resource_submit_status.id
                            geo_spatial_resource.resource_submitter_id = resource.submitter_id
                            geo_spatial_resource.submitter_id = resource.submitter_id

                            # parsed template field?
                            parsed_data.resource_detail_guid = geo_spatial_resource.submitter_id

                            resource_submit_status = self.pcor_ingest.create_geo_spatial_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_data_resource=geo_spatial_resource
                            )

                            # check status and bail if not success
                            if not resource_submit_status.success:
                                logger.error(
                                    "creation of geospatial_data_resource failed, bailing: %s" % resource_submit_status.message)
                                parsed_data.success = False
                                parsed_data.errors += resource_submit_status.errors
                                parsed_data.message = resource_submit_status.message
                                parsed_data.path_url = resource_submit_status.path_url
                                parsed_data.response_content = resource_submit_status.response_content
                                parsed_data.request_content = resource_submit_status.request_content
                                return

                            resource.resource_type = model_data['geospatial_data_resource'].display_type

                            discovery = self.pcor_ingest.create_discovery_from_resource(program.name, project, resource,
                                                                                        geo_spatial_resource)
                            discovery.comment = geo_spatial_resource.comments  # intended use?

                            for item in geo_spatial_resource.measures:
                                filter = AdvSearchFilter()
                                filter.key = "Measures"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)


                            if geo_spatial_resource.exposure_media:
                                filter = AdvSearchFilter()
                                filter.key = "Exposures"
                                filter.value = geo_spatial_resource.exposure_media
                                discovery.adv_search_filters.append(filter)

                            logger.info("created discovery: %s" % discovery)
                            discovery_result = self.pcor_ingest.decorate_resc_with_discovery(discovery)
                            logger.info("discovery_result: %s" % discovery_result)

                        if 'population_data_resource' in model_data.keys():
                            logger.info('process:: adding pop_data_resource')
                            pop_data_resource = model_data['population_data_resource']
                            pop_data_resource.resource_id = resource_submit_status.id
                            pop_data_resource.resource_submitter_id = resource.submitter_id
                            pop_data_resource.submitter_id = resource.submitter_id

                            resource_submit_status = self.pcor_ingest.create_pop_data_resource(
                                program_name=program.name,
                                project_name=project.name,
                                pop_data_resource=pop_data_resource
                            )

                            if not resource_submit_status.success:
                                logger.error("creation of population_data_resource failed, bailing: %s" %
                                             resource_submit_status)
                                parsed_data.success = False
                                parsed_data.errors += resource_submit_status.errors
                                parsed_data.message = resource_submit_status.response.text
                                parsed_data.path_url = resource_submit_status.path_url
                                parsed_data.response_content = resource_submit_status.response_content
                                parsed_data.request_content = resource_submit_status.request_content
                                return

                            resource.resource_type = model_data['population_data_resource'].display_type

                            discovery = self.pcor_ingest.create_discovery_from_resource(program.name, project, resource,
                                                                                        pop_data_resource)
                            discovery.comment = pop_data_resource.comments  # intended use?

                            for item in pop_data_resource.exposures:
                                filter = AdvSearchFilter()
                                filter.key = "Exposures"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            for item in pop_data_resource.population_studied:
                                filter = AdvSearchFilter()
                                filter.key = "Population"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            for item in pop_data_resource.population_studied_other:
                                filter = AdvSearchFilter()
                                filter.key = "Population"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            logger.info("created discovery: %s" % discovery)
                            discovery_result = self.pcor_ingest.decorate_resc_with_discovery(discovery)
                            logger.info("discovery_result: %s" % discovery_result)

                        if 'geospatial_tool_resource' in model_data.keys():
                            logger.info('process:: adding geo_tool_resource')
                            geo_tool_resource = model_data['geospatial_tool_resource']
                            geo_tool_resource.resource_id = resource_submit_status.id
                            geo_tool_resource.resource_submitter_id = resource.submitter_id
                            geo_tool_resource.submitter_id = resource.submitter_id

                            self.pcor_ingest.create_geo_spatial_tool_resource(
                                program_name=program.name,
                                project_name=project.name,
                                geo_spatial_tool_resource=geo_tool_resource
                            )

                            if not resource_submit_status.success:
                                logger.error("creation of geospatial_data_resource failed, bailing: %s"
                                             % resource_submit_status)
                                parsed_data.success = False
                                parsed_data.message = resource_submit_status.response.text
                                parsed_data.errors += resource_submit_status.errors
                                parsed_data.path_url = resource_submit_status.path_url
                                parsed_data.response_content = resource_submit_status.response_content
                                parsed_data.request_content = resource_submit_status.request_content
                                return

                            resource.resource_type = model_data['geospatial_tool_resource'].display_type

                            discovery = self.pcor_ingest.create_discovery_from_resource(program.name, project, resource,
                                                                                        geo_tool_resource)
                            discovery.comment = geo_tool_resource.intended_use  # intended use?

                            for item in geo_tool_resource.tool_type:
                                filter = AdvSearchFilter()
                                filter.key = "Tool_Type"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            for item in geo_tool_resource.operating_system:
                                filter = AdvSearchFilter()
                                filter.key = "Operating_System"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            for item in geo_tool_resource.languages:
                                filter = AdvSearchFilter()
                                filter.key = "Languages"
                                filter.value = item
                                discovery.adv_search_filters.append(filter)

                            logger.info("created discovery: %s" % discovery)
                            discovery_result = self.pcor_ingest.decorate_resc_with_discovery(discovery)
                            logger.info("discovery_result: %s" % discovery_result)

        except requests.HTTPError as exception:
            logger.error('unexpected Error occurred: %s' % str(exception))
            parsed_data.success = False
            pcor_error = PcorError()
            pcor_error.type = ""
            pcor_error.key = ""
            pcor_error.message = str(exception)
            pcor_error.traceback = traceback.format_exc(exception)
            parsed_data.errors.append(pcor_error)
