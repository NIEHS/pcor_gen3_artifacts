import logging
import json
import re
import os

import requests
from requests import HTTPError

from urllib.parse import quote

from gen3.metadata import Gen3Metadata
from gen3.submission import Gen3Submission
from pcor_ingest.gen3auth import PcorGen3Auth
from jinja2 import Environment, PackageLoader, select_autoescape

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, SubmitResponse, PcorDiscoveryMetadata, \
    Tag, AdvSearchFilter, PcorIntermediateProgramModel
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError

logger = logging.getLogger(__name__)


class PcorGen3Ingest:
    """
    Library for ingesting data into PCOR
    """

    def __init__(self, pcor_ingest_configuration, gen3_auth=None):
        """
        Initialize ingest tool
        :param pcor_ingest_configuration: IngestConfiguration with Gen3 server properties
        :param gen3_auth: Optional Gen3Auth object if auth is done
        :return:
        """

        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.gen3_auth = gen3_auth
        self.env = Environment(loader=PackageLoader('pcor_ingest', 'templates'))

        self.env.filters['jsonify'] = json.dumps

        if not gen3_auth:
            logger.info('doing auth')
            pcor_gen3_auth = PcorGen3Auth(pcor_ingest_configuration)
            self.gen3_auth = pcor_gen3_auth.authenticate_to_gen3()
            logger.info("authenticated to Gen3")

    def create_program(self, program):
        """
        Creates a program in gen3
        :param program: data structure representing the program
        :return: on success return program id
        """
        logger.info('adding program:%s' % program)
        sub = Gen3Submission(self.gen3_auth)
        program_json = self.produce_program_json(program)

        response = sub.create_program(json.loads(program_json))
        program_id = response["id"]
        logger.info("program created with id:%s" % program_id)
        return program_id

    def create_project(self, program, pcor_intermediate_project_model):
        """
        :param program: identifier of the program in Gen3
        :param pcor_intermediate_project_model: data structure representing project data
        :return: on success returns project id
        """
        logger.info('create_project()')
        sub = Gen3Submission(self.gen3_auth)
        project = pcor_intermediate_project_model.name

        existing_projects = self.get_projects(program)
        project_already_exist = self.check_project_exists(existing_projects, project)
        if project_already_exist:
            logger.info('Project already exists: %s', project)
            logger.info('fetch project details')
            project_query_result = self.get_individual_project_info(project_code=project)
            project_id = project_query_result.id
            return project_id

        else:
            logger.info('Creating project: %s', project)
            project_json = self.produce_project_json(pcor_intermediate_project_model)
            response = sub.create_project(quote(program), json.loads(project_json))
            project_id = response["entities"][0]["id"]
            logger.info("project_id: %s" % project_id)
            return project_id

    def delete_project(self, program, project_name):
        """
        :param program: identifier of the program in Gen3
        :param project_name: project dbgap_accession number
        :return: void
        """
        logger.info("delete_project()")
        sub = Gen3Submission(self.gen3_auth)

        try:
            response = sub.delete_project(program, project_name)
        except requests.exceptions.HTTPError:
            logger.warn("error, project not found")

    def create_resource(self, program_name, project_name, resource):
        """
        Add (or update) a resource
        :param program_name:  name of program (e.g. NFS)
        :param project_name: name of project (code)
        :param resource: PcorIntermediateResourceModel representing the resource
        :return:on success returns resource id or None in failure
        """

        logger.info('create_resource()')
        sub = Gen3Submission(self.gen3_auth)

        # add project info

        pcor_intermediate_project_model = self.pcor_project_model_from_id(project_name)
        resource.project = pcor_intermediate_project_model

        json_string = self.produce_resource_json(resource)
        logger.debug("json_string: %s" % json_string)
        resource_json = json.loads(json_string)
        logger.info('adding resource to program: {}, project: {}'.format(program_name, project_name))
        status = self.submit_record(program=program_name, project=project_name, json_data=resource_json)
        logger.info(status)
        resource.id = status.id
        return status

    def create_discovery_from_resource(self, program_name, project, resource, geo_spatial_resource):
        """
        Given a project and resource derive the discovery
         model data (to be augmented based on the subtype)

         :param program_name
         :param project: PcorIntermediateProjectModel
         :param resource: PcorIntermediateResourceModel
         :return: PcorDiscoveryMetadata with the metadata that can be derived
        from the given model data
        """
        logger.info("create_discovery_from_resource()")

        logger.info("looking up program: %")

        program = self.get_individual_program_info(program_name)

        discovery = PcorDiscoveryMetadata()
        discovery.program_name = program_name
        discovery.project_description = project.description
        discovery.name = resource.name
        discovery.description = resource.description
        discovery.publications = resource.publications
        discovery.domain = ','.join(resource.domain)
        discovery.has_api = "false"
        discovery.type = resource.resource_type
        discovery.has_visualization_tool = "false"
        discovery.is_citizen_collected = "false"
        discovery.resource_use_agreement = resource.resource_use_agreement
        discovery.resource_id = resource.id
        discovery.resource_url = resource.resource_url

        # migrate keywords that are available in resource
        for kw in resource.keywords:
            if kw:
                tag = Tag()
                tag.name = kw
                tag.category = "Keyword"
                discovery.tags.append(tag)

        for item in resource.domain:
            if item:
                tag = Tag()
                tag.name = item
                tag.category = "Domain"
                discovery.tags.append(tag)


        tag = Tag()
        tag.name = discovery.type
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = program_name
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Domain"
        filter.value = resource.domain
        discovery.adv_search_filters.append(filter)

        '''
        for item in resource.domain:
            filter = AdvSearchFilter()
            filter.key = "Measures"
            filter.value = item
            discovery.adv_search_filters.append(filter)

        '''
        for item in geo_spatial_resource.measures:
            filter = AdvSearchFilter()
            filter.key = "Measures"
            filter.value = item
            discovery.adv_search_filters.append(filter)

        for item in geo_spatial_resource.exposure_media:
            filter = AdvSearchFilter()
            filter.key = "Exposure Media"
            filter.value = item
            discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = resource.resource_type
        discovery.adv_search_filters.append(filter)

        return discovery

    def decorate_resc_with_discovery(self, discovery_data):
        """
        Add discovery metadata for the given resource
        :param discovery_data: PcorDiscoveryMetadata
        :return: Response (just the json for now)
        """

        logger.info("decorate_resc_with_discovery()")
        json_string = self.produce_discovery_json(discovery_data)
        logger.debug("json_string: %s" % json_string)
        discovery_json = json.loads(json_string)
        discoverable_data = dict(_guid_type="discovery_metadata", gen3_discovery=discovery_json)

        logger.info('adding discovery data')
        metadata = Gen3Metadata(self.gen3_auth)
        response = metadata.create(discovery_data.resource_id, discoverable_data, aliases=None, overwrite=True)
        return response

    def create_geo_spatial_data_resource(self, program_name, project_name, geo_spatial_data_resource):
        logger.info("create_geo_spatial_data_resource()")

        pcor_intermediate_project_model = self.pcor_project_model_from_id(project_name)
        geo_spatial_data_resource.project = pcor_intermediate_project_model

        json_string = self.produce_geo_spatial_data_resource(geo_spatial_data_resource)
        logger.debug("json_string: %s" % json_string)
        geo_spatial_data_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_name, json_data=geo_spatial_data_resource_json)
        logger.info(status)
        return status

    def create_geo_spatial_tool_resource(self, program_name, project_name, geo_spatial_tool_resource):
        logger.info("create_geo_spatial_tool_resource()")
        self.get_individual_project_info(project_name)

        pcor_intermediate_project_model = self.pcor_project_model_from_id(project_name)
        geo_spatial_tool_resource.project = pcor_intermediate_project_model

        json_string = self.produce_geo_spatial_tool_resource(geo_spatial_tool_resource)
        logger.debug("json_string: %s" % json_string)
        geo_spatial_tool_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_name, json_data=geo_spatial_tool_resource_json)
        logger.info(status)
        return status

    def create_pop_data_resource(self, program_name, project_name, pop_data_resource):
        logger.info("create_pop_data_resource()")

        pcor_intermediate_project_model = self.pcor_project_model_from_id(project_name)
        pop_data_resource.project = pcor_intermediate_project_model

        json_string = self.produce_pop_data_resource(pop_data_resource)
        logger.info("json_string: %s" % json_string)
        pop_data_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_name, json_data=pop_data_resource_json)
        logger.info(status)
        return status

    ############################################
    # json from template methods
    ############################################
    def produce_program_json(self, program):
        """
        Produce the json of a program from the jinja template
        :param program: PcorIntermediateProgramModel of a program
        :return: string with project JSON for loading into Gen3
        """
        logger.info("produce_program_json()")
        template = self.env.get_template("program.jinja")
        rendered = template.render(program=program).replace('"none"', 'null').replace('"None"', 'null')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_program_json(self, program):

        """
        Produce the json of a pgogram from the jinja template
        :param program: PcorProgramModel of a project
        :return: string with project JSON for loading into Gen3
        """
        logger.info("produce_program_json()")
        template = self.env.get_template("program.jinja")
        rendered = template.render(program=program).replace('"none"', 'null').replace('"None"', 'null')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_project_json(self, project):
        """
        Produce the json of a project from the jinja template
        :param project: PcorIntermediateProjectModel of a project
        :return: string with project JSON for loading into Gen3
        """
        logger.info("produce_project_json()")
        template = self.env.get_template("project.jinja")
        rendered = template.render(model=project).replace('"none"', 'null').replace('"None"', 'null').replace('"nan"', 'null')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_resource_json(self, resource):
        """
        Render resource data as JSON via template
        :param resource: PcorIntermediateResourceModel representing the resource data
        :return: string with resource JSON for loading into Gen3
        """
        logger.info("produce_resource_json()")
        template = self.env.get_template("resource.jinja")
        rendered = template.render(resource=resource).replace('"none"', 'null').replace('"None"', 'null').replace('False', 'false').replace('True', 'true')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_discovery_json(self, discovery_data):
        """
        Render discovery data as JSON via template
        :param discovery_data: PcorDiscoveryMetadata representing the resource data for discovery page
        :return: string with JSON for loading into Gen3
        """
        logger.info("produce_discovery_json()")
        template = self.env.get_template("discoverymd.jinja")
        rendered = template.render(discovery=discovery_data)
        return rendered

    def produce_geo_spatial_data_resource(self, geo_spatial_data_resource):
        """
        Render geo_spatial_data_resource  as JSON via template
        :param geo_spatial_data_resource: PcorGeospatialDataResourceModel representing the geo-spatial data
        :return: string with resource JSON for loading into Gen3
        """

        logger.info("produce_geo_spatial_data_resource()")
        template = self.env.get_template("geospatial_data_resource.jinja")
        rendered = template.render(geo_spatial_data_resource=geo_spatial_data_resource).replace('"none"', 'null')\
            .replace('"None"', 'null').replace('False', 'false').replace('True', 'true').replace(u'\xa0', '')\
            .replace('\'', '')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_geo_spatial_tool_resource(self, geo_spatial_tool_resource):
        """
        Render geo_spatial_tool_resource  as JSON via template
        :param geo_spatial_tool_resource: PcorGeospatialToolResourceModel representing the geo-spatial tool
        :return: string with resource JSON for loading into Gen3
        """
        logger.info("produce_geo_spatial_tool_resource()")
        template = self.env.get_template("geospatial_tool_resource.jinja")
        rendered = template.render(geo_tool_resource=geo_spatial_tool_resource)
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_pop_data_resource(self, pop_data_resource):
        """
        Render pop_data_resource  as JSON via template
        :param pop_data_resource: PcorPopDataResourceModel representing the population data
        :return: string with resource JSON for loading into Gen3
        """
        logger.info("produce_pop_data_resource()")
        template = self.env.get_template("population_data_resource.jinja")
        rendered = template.render(pop_data_resource=pop_data_resource)
        logger.info("rendered: %s" % rendered)
        return rendered

    #############################################
    # supporting methods
    ###########################################
    @staticmethod
    def check_program_exists( existing_programs, program):
        """
        :param existing_programs:
        :param program:
        :return:
        """
        program_already_exist = False
        if existing_programs and 'links' in existing_programs:
            for entry in existing_programs['links']:
                temp_project = entry.split('/')[-1]
                if temp_project == program:
                    program_already_exist = True
        return program_already_exist

    @staticmethod
    def check_project_exists(existing_projects, project):
        """

        :param existing_projects:
        :param project:
        :return:
        """
        project_already_exist = False
        if existing_projects and 'links' in existing_projects:
            for entry in existing_projects['links']:
                temp_project = entry.split('/')[-1]
                if temp_project == project:
                    project_already_exist = True
        return project_already_exist

    def retrieve_project_files_tsv(self, project, program, node_type, export_file):
        """
        Export the nodes as tsv
        :param project: project identifier
        :param program: program identifier
        :param node_type: type of Gen3 node
        :param export_file: location of downloaded file
        :return: export file
        """
        logger.info('retrieve_project_files_tsv()')
        sub = Gen3Submission(self.gen3_auth)
        sub.export_node(program, project, node_type, "tsv", filename=export_file)

    def get_projects(self, program=None):
        """
        :param program: GEN3 program defaults to one in property file
        :return: dict of projects with project links
        """
        logger.info('get_projects()')
        if program is None:
            program = self.program
        sub = Gen3Submission(self.gen3_auth)
        projects = sub.get_projects(program)
        return projects

    def pcor_project_model_from_id(self, project_submitter_id):
        """
        Given a project submitter id, build a skeleton project model with id and other info
        :param project_submitter_id: code for project
        :return: pcor_intermediate_project_model with project info
        """
        return self.get_individual_project_info(project_submitter_id)

    def get_individual_program_info(self, program_name):
        """
        Do a query to get program details
        :param program_name: name field in program
        :return: PCORIntermediateProgramModel
        """
        json = """{{
                 program(name: "{}") {{
                   id
                   name
                   dbgap_accession_number
                 }}
               }}
               """.format(program_name)
        logger.info("query:{}".format(json))

        sub = Gen3Submission(self.gen3_auth)
        result = sub.query(json)
        logger.info("result:{}".format(result))

        program = PcorIntermediateProgramModel()
        program.id = result["data"]["program"][0]["id"]
        program.program_name = result["data"]["program"][0]["name"]
        program.dbgap_accession_number = result["data"]["program"][0]["dbgap_accession_number"]

        return program

    def get_individual_project_info(self, project_code):
        """
        Do a query to get code, id, and name of a project based on the project code
        :param project_code: code field in project
        :return: JSON with query result
        """

        query = """{{
         project(code: "{}") {{
           id
           code
           name
           long_name
           investigator_affiliation
           investigator_name
           availability_mechanism
           availability_type
           support_source
           support_id
           dbgap_accession_number
           submitter_id
           complete
           project_url
           description
         }}
       }}
       """.format(project_code)
        logger.info("query:{}".format(json))

        sub = Gen3Submission(self.gen3_auth)
        result = sub.query(query)
        logger.info("result:{}".format(result))

        project = PcorIntermediateProjectModel()
        project.name = result["data"]["project"][0]["name"]
        project.project_code = result["data"]["project"][0]["code"]
        project.investigator_name = result["data"]["project"][0]["investigator_name"]
        project.investigator_affiliation = result["data"]["project"][0]["investigator_affiliation"]
        project.long_name = result["data"]["project"][0]["long_name"]
        project.support_source = result["data"]["project"][0]["support_source"]
        project.support_id = result["data"]["project"][0]["support_id"]
        project.project_url = result["data"]["project"][0]["project_url"]
        project.dbgap_accession_number = result["data"]["project"][0]["dbgap_accession_number"]
        project.id = result["data"]["project"][0]["id"]
        return project

    def submit_record(self, program, project, json_data):
        """
        :param program: The program to submit to.
        :param project: The project to submit to.
        :param json_data: The json defining the record(s) to submit. For multiple records, the json should be an
        array of records.
        :return:
        """
        logger.info('submit_record()')
        sub = Gen3Submission(self.gen3_auth)
        try:
            status_response = sub.submit_record(program, project, json_data)
            logger.info("status_response: %s", str(status_response))
            submission_status = PcorProcessResult()

            submission_status.id = status_response["entities"][0]["id"]
            submission_status.type = status_response["entities"][0]["type"]

            # unique_keys are different on project vs resource creation
            unique_keys = status_response["entities"][0]["unique_keys"][0]
            submission_status.submitter_id = unique_keys.get("submitter_id")
            submission_status.project_id = unique_keys.get("project_id")
            submission_status.program_name = program
            submission_status.project_name = project
            # TODO: augment sub status
            return submission_status
        except HTTPError as pcor_error:
            logger.error("error in submission:%s" % pcor_error)
            submission_status = PcorProcessResult()
            submission_status.success = False
            submission_status.program_name = program
            submission_status.project_code = project
            submission_status.request_content = pcor_error.request
            submission_status.response_content = json.loads(pcor_error.response.content)

            for entity in submission_status.response_content["entities"]:
                for error_entry in entity["errors"]:

                    error = PcorError()

                    if len(error_entry["keys"]) > 0:
                        error.key = error_entry["keys"][0]

                    error.message = error_entry["message"]
                    error.type = error_entry["type"]
                    submission_status.errors.append(error)

            submission_status.path_url = submission_status.request_content.path_url
            submission_status.program_name = program
            submission_status.project_name = project
            submission_status.message = submission_status.response_content["message"]

            # program_name, program_submitter_id, project_id, project_name

            return submission_status
