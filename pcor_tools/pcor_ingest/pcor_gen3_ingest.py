import json
import logging
import os
import traceback
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
from requests import HTTPError

from gen3.metadata import Gen3Metadata
from gen3.submission import Gen3Submission
from pcor_ingest.gen3auth import PcorGen3Auth
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorDiscoveryMetadata, \
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

        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the relative path to your template directory
        template_rel_path = 'templates'

        # Construct the absolute path to the template directory
        template_dir = os.path.join(script_dir, template_rel_path)

        # Create a Jinja environment with the FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug('template_dir: %s' % template_dir)
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

    def delete_program(self, program):
        """
        Delete a program
        :param program: name of program
        """
        logger.info("delete_program()")
        sub = Gen3Submission(self.gen3_auth)
        try:
            logger.info('\n\n\n\n===================Start deleting program====================================')
            logger.info('deleting program: %s', program)
            response = sub.delete_program(program)
            logger.info('response: %s', response)
            logger.info('\n===================Finished deleting program====================================\n\n\n\n')
            return response
        except Exception as pcor_error:
            logger.error("error, program not found:%s" % pcor_error)

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
            self.resubmission_cleanups(program=program, project=project)

        logger.info('Creating project: %s', project)
        project_json = self.produce_project_json(pcor_intermediate_project_model)
        response = sub.create_project(quote(program), json.loads(project_json))
        project_id = response["entities"][0]["id"]
        logger.info("project_id: %s" % project_id)
        return project_id

    def delete_project(self, program, project_code):
        """
        :param program: identifier of the program in Gen3
        :param project_code: project dbgap_accession number
        :return: void
        """
        logger.info("delete_project()")
        sub = Gen3Submission(self.gen3_auth)

        try:
            logger.info('\n\n\n\n===================Start deleting project====================================')
            logger.info('deleting project: %s', project_code)
            response = sub.delete_project(program, project_code)
            logger.info('response: %s', response)
            logger.info('\n===================Finished deleting project====================================\n\n\n\n')
            return response
        except Exception as pcor_error:
            logger.error("error, project not found:%s" % pcor_error)

    def create_resource(self, program_name, project_code, resource):
        """
        Add (or update) a resource
        :param program_name:  name of program (e.g. NFS)
        :param project_code: name of project (code)
        :param resource: PcorIntermediateResourceModel representing the resource
        :return:on success returns resource id or None in failure
        """

        logger.info('create_resource()')
        sub = Gen3Submission(self.gen3_auth)

        # add project info

        pcor_intermediate_project_model = self.pcor_project_model_from_code(project_code)
        resource.project = pcor_intermediate_project_model

        json_string = self.produce_resource_json(resource)
        logger.debug("json_string: %s" % json_string)
        resource_json = json.loads(json_string)
        logger.info('adding resource to program: {}, project: {}'.format(program_name, project_code))
        status = self.submit_record(program=program_name, project=project_code, json_data=resource_json)
        logger.info(status)
        resource.id = status.id
        return status

    @staticmethod
    def create_discovery_from_resource(program, project, resource, data_resource):
        """
        Given a project and resource derive the discovery
         model data (to be augmented based on the subtype)

         :param program
         :param project: PcorIntermediateProjectModel
         :param resource: PcorIntermediateResourceModel
         :return: PcorDiscoveryMetadata with the metadata that can be derived
        from the given model data
        """
        logger.info("create_discovery_from_resource()")

        discovery = PcorDiscoveryMetadata()
        discovery.program_name = program.name
        discovery.project_sponsor = ','.join(project.project_sponsor)
        discovery.project_name = project.name
        discovery.project_short_name = project.short_name
        discovery.project_url = project.project_url
        discovery.project_sponsor_type = project.project_sponsor_type

        '''
        if discovery.project_name == resource.name:
            discovery.name = resource.name
        else:
            discovery.name = discovery.project_name + ":" + resource.name
        '''
        discovery.name = project.short_name

        discovery.payment_required = resource.payment_required
        discovery.verification_datetime = resource.verification_datetime
        discovery.description = resource.description
        discovery.resource_id = resource.id
        discovery.resource_url = resource.resource_url
        discovery.type = resource.resource_type
        if discovery.type:
            search_filter = AdvSearchFilter()
            search_filter.key = "Resource Type"
            search_filter.value = discovery.type
            discovery.adv_search_filters.append(search_filter)

            tag = Tag()
            tag.name = discovery.type
            tag.category = "Resource Type"
            discovery.tags.append(tag)

        discovery.domain = ', '.join(resource.domain)
        if hasattr(resource, 'domain_other'):
            discovery.domain_other = ', '.join(resource.domain_other) if resource.domain_other else None
        discovery.publications = resource.publications
        discovery.publication_links = resource.publication_links

        for sponsor_type in discovery.project_sponsor_type:
            search_filter = AdvSearchFilter()
            search_filter.key = "Sponsor Type"
            search_filter.value = sponsor_type
            discovery.adv_search_filters.append(search_filter)

        if len(resource.publications) > 0:
            discovery.publications_1 = resource.publications[0]

        if len(resource.publications) > 1:
            discovery.publications_2 = resource.publications[1]

        if len(resource.publications) > 2:
            discovery.publications_3 = resource.publications[2]

        if len(resource.publication_links) > 0:
            discovery.publication_link_1 = resource.publication_links[0]

        if len(resource.publication_links) > 1:
            discovery.publication_link_2 = resource.publication_links[1]

        if len(resource.publication_links) > 2:
            discovery.publication_link_3 = resource.publication_links[2]

        '''
        if resource.resource_reference:
            discovery.resource_reference_1 = resource.resource_reference[0]

        if len(resource.resource_reference) > 1:
            discovery.resource_reference_2 = resource.resource_reference[2]
        '''

        discovery.keywords = ','.join(resource.keywords)
        discovery.payment_required = resource.payment_required
        discovery.created_datetime = resource.created_datetime
        discovery.updated_datetime = resource.updated_datetime
        discovery.resource_reference = resource.resource_reference
        discovery.resource_use_agreement = resource.resource_use_agreement
        discovery.resource_use_agreement_link = resource.resource_use_agreement_link

        if data_resource:
            if hasattr(data_resource, 'has_api'):
                discovery.has_api = data_resource.has_api
            if hasattr(data_resource, 'has_visualization_tool'):
                discovery.has_visualization_tool = data_resource.has_visualization_tool
            if hasattr(data_resource, 'is_citizen_collected'):
                discovery.is_citizen_collected = data_resource.includes_citizen_collected
            if hasattr(data_resource, 'data_formats'):
                discovery.data_formats = ', '.join(data_resource.data_formats) if data_resource.data_formats else None
            if hasattr(data_resource, 'spatial_resolution'):
                discovery.spatial_resolution = ', '.join(data_resource.spatial_resolution) if data_resource.spatial_resolution else None
                for item in data_resource.spatial_resolution:
                    if data_resource.spatial_resolution:
                        if data_resource.spatial_resolution != "Other":
                            search_filter = AdvSearchFilter()
                            search_filter.key = "Spatial Resolution"
                            search_filter.value = item
                            discovery.adv_search_filters.append(search_filter)
            if hasattr(data_resource, 'spatial_resolution_other'):
                discovery.spatial_resolution_other = ', '.join(data_resource.spatial_resolution_other) if data_resource.spatial_resolution_other else None
            if hasattr(data_resource, 'spatial_coverage'):
                discovery.spatial_coverage = ', '.join(data_resource.spatial_coverage) if data_resource.spatial_coverage else None
            if hasattr(data_resource, 'spatial_coverage_other'):
                discovery.spatial_coverage_other = ', '.join(data_resource.spatial_coverage_other) if data_resource.spatial_coverage_other else None
            if hasattr(data_resource, 'temporal_resolution'):
                discovery.temporal_resolution = ', '.join(data_resource.temporal_resolution) if data_resource.temporal_resolution else None
                for item in data_resource.temporal_resolution:
                    if data_resource.temporal_resolution:
                        if data_resource.temporal_resolution != "Other":
                            search_filter = AdvSearchFilter()
                            search_filter.key = "Temporal Resolution"
                            search_filter.value = item
                            discovery.adv_search_filters.append(search_filter)
            if hasattr(data_resource, 'temporal_resolution_other'):
                discovery.temporal_resolution_other = ', '.join(data_resource.temporal_resolution_other) if data_resource.temporal_resolution_other else None
            if hasattr(data_resource, 'geometry_type'):
                discovery.geometry_type = ', '.join(data_resource.geometry_type) if data_resource.geometry_type else None
                for item in data_resource.geometry_type:
                    search_filter = AdvSearchFilter()
                    search_filter.key = "Geometry Type"
                    search_filter.value = item
                    discovery.adv_search_filters.append(search_filter)
            if hasattr(data_resource, 'tool_type'):
                discovery.tool_type = ', '.join(data_resource.tool_type) if data_resource.tool_type else None
            if hasattr(data_resource, 'comments'):
                discovery.comments = data_resource.comments if data_resource.comments else None
            if hasattr(data_resource, 'time_extent_start_yyyy'):
                discovery.time_extent_start_yyyy = data_resource.time_extent_start_yyyy if data_resource.time_extent_start_yyyy else None
            if hasattr(data_resource, 'time_extent_end_yyyy'):
                discovery.time_extent_end_yyyy = data_resource.time_extent_end_yyyy if data_resource.time_extent_end_yyyy else None
            if hasattr(data_resource, 'time_available_comment'):
                discovery.time_available_comment = data_resource.time_available_comment if data_resource.time_available_comment else None

            if hasattr(data_resource, 'intended_use'):
                discovery.intended_use = data_resource.intended_use if data_resource.intended_use else None

            if hasattr(data_resource, 'data_location_text'):
                if len(data_resource.data_location_text) > 0:
                    discovery.data_location_text_1 = data_resource.data_location_text[0]

                if len(data_resource.data_location_text) > 1:
                    discovery.data_location_text_2 = data_resource.data_location_text[1]

                if len(data_resource.data_location_text) > 2:
                    discovery.data_location_text_3 = data_resource.data_location_text[2]
            if hasattr(data_resource, 'data_link'):
                if len(data_resource.data_link) > 0:
                    discovery.data_location_link_1 = data_resource.data_link[0]

                if len(data_resource.data_link) > 1:
                    discovery.data_location_link_2 = data_resource.data_link[1]

                if len(data_resource.data_link) > 2:
                    discovery.data_location_link_3 = data_resource.data_link[2]

            if hasattr(data_resource, 'source_name'):
                discovery.source_name = data_resource.source_name if data_resource.source_name else None

        for item in resource.access_type:
            if item:
                search_filter = AdvSearchFilter()
                search_filter.key = "Access Type"
                search_filter.value = item
                discovery.adv_search_filters.append(search_filter)

        # migrate keywords that are available in resource
        for item in resource.keywords:
            if item:
                if PcorGen3Ingest.check_tag_present(item, discovery.tags):
                    continue
                tag = Tag()
                tag.name = item
                tag.category = "Keyword"
                discovery.tags.append(tag)

        for item in resource.domain:
            if item:
                if PcorGen3Ingest.check_tag_present(item, discovery.tags):
                    continue
                else:
                    tag = Tag()
                    tag.name = item
                    tag.category = "Domain"
                    discovery.tags.append(tag)

        filter_project_sponsor_list = [
            "United States Forestry Service (USFS)",
            "United States Department of Agriculture (USDOA)",
            "United States Department of the Interior (USDOI)",
            "United States Geological Survey (USGS)",
            "National Aeronautics and Space Administration (NASA)",
            "Department of Homeland Security (USDHS)",
            "Centers for Disease Control and Prevention (CDC)",
            "Department of Commerce (USDOC)",
            "Federal Emergency Management Agency (FEMA)",
            "National Oceanic and Atmospheric Administration (NOAA)",
            "Center for Disease Control (CDC)",
            "Department of Health and Human Services (DHHS)",
            "Agency for Healthcare Research and Quality (AHRQ)",
            "United States Census Bureau (US Census)",
            "Environmental Protection Agency (EPA)",
            "National Weather Service (NWS)"
        ]

        sponsor_no_match = False

        for sponsor in project.project_sponsor:
            if sponsor in filter_project_sponsor_list:
                search_filter = AdvSearchFilter()
                search_filter.key = "Project Sponsor"
                search_filter.value = sponsor
                discovery.adv_search_filters.append(search_filter)
            else:
                sponsor_no_match = True
        if sponsor_no_match:
            search_filter = AdvSearchFilter()
            search_filter.key = "Project Sponsor"
            search_filter.value = "Other"
            discovery.adv_search_filters.append(search_filter)
            
        return discovery

    def decorate_resc_with_discovery(self, discovery_data):
        """
        Add discovery metadata for the given resource
        :param discovery_data: PcorDiscoveryMetadata
        :return: Response (just the json for now)
        """

        logger.info("decorate_resc_with_discovery()")
        # remove Other tag if it exists

        for tag in discovery_data.tags:
            if tag.name == 'Other':
                discovery_data.tags.remove(tag)

        json_string = self.produce_discovery_json(discovery_data)
        logger.debug("json_string: %s" % json_string)
        discovery_json = json.loads(json_string)
        logger.info('discovery_json: %s', discovery_json)

        # validation check
        existing_discovery_entries = self.get_discovery_entries()
        discovery_entry_already_exists, existing_discovery_entry_guid = self.check_discovery_entry_exists(
            existing_discovery_entries=existing_discovery_entries,
            new_entry=discovery_json)
        if discovery_entry_already_exists and existing_discovery_entry_guid is not None:
            logger.info('Discovery entry already exists. Recreating...')
            logger.info('Deleting metadata entry guid: %s' % existing_discovery_entry_guid)
            self.delete_discovery_metadata_with_guid(existing_discovery_entry_guid)

        logger.info('Creating a new entry...')
        discoverable_data = dict(_guid_type="discovery_metadata", gen3_discovery=discovery_json)
        logger.info('adding discovery data')
        metadata = Gen3Metadata(self.gen3_auth)
        response = metadata.create(discovery_data.resource_id, discoverable_data, aliases=None, overwrite=True)
        ''' cgymeyer submit_mds()
        metadata = Gen3Expansion(auth_provider=self.gen3_auth,
                                 submission=Gen3Submission('https://staging.chordshealth.org/', self.gen3_auth),
                                 endpoint='https://staging.chordshealth.org/')
        mds = Gen3Metadata(auth_provider=self.gen3_auth)
        discovery_mds = mds.create(discovery_data.resource_id, discoverable_data, overwrite=True)
        response = metadata.submit_mds(mds=discovery_mds)
        '''
        return response

    def delete_discovery_metadata_with_guid(self, guid):
        """
        Delete discovery metadata for the given guid
        :param guid: Metadata entry guid to be deleted
        :return: Response (just the json for now)
        """
        logger.info("delete_discovery_metadata_with_guid()")
        logger.info('\n\n\n\n===================Start deleting discovery metadata entry===============================')
        logger.info('guid: %s' % guid)
        metadata = Gen3Metadata(self.gen3_auth)
        response = metadata.delete(guid=guid)
        logger.info('response: %s' % response)
        logger.info('\n===================Finished deleting discovery metadata entry============================\n\n\n\n')
        return response

    def create_geo_spatial_data_resource(self, program_name, project_code, geo_spatial_data_resource):
        logger.info("create_geo_spatial_data_resource()")

        pcor_intermediate_project_model = self.pcor_project_model_from_code(project_code)
        geo_spatial_data_resource.project = pcor_intermediate_project_model

        json_string = self.produce_geo_spatial_data_resource(geo_spatial_data_resource)
        logger.debug("json_string: %s" % json_string)
        geo_spatial_data_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_code,
                                    json_data=geo_spatial_data_resource_json)
        logger.info(status)
        return status

    def create_geo_spatial_tool_resource(self, program_name, project_code, geo_spatial_tool_resource):
        logger.info("create_geo_spatial_tool_resource()")

        pcor_intermediate_project_model = self.pcor_project_model_from_code(project_code)
        geo_spatial_tool_resource.project = pcor_intermediate_project_model

        json_string = self.produce_geo_spatial_tool_resource(geo_spatial_tool_resource)
        logger.debug("json_string: %s" % json_string)
        geo_spatial_tool_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_code,
                                    json_data=geo_spatial_tool_resource_json)
        logger.info(status)
        return status

    def create_pop_data_resource(self, program_name, project_code, pop_data_resource):
        logger.info("create_pop_data_resource()")

        pcor_intermediate_project_model = self.pcor_project_model_from_code(project_code)
        pop_data_resource.project = pcor_intermediate_project_model

        json_string = self.produce_pop_data_resource(pop_data_resource)
        logger.info("json_string: %s" % json_string)
        pop_data_resource_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_code, json_data=pop_data_resource_json)
        logger.info(status)
        return status

    def create_key_dataset(self, program_name, project_code, key_dataset):
        logger.info("create_key_dataset()")

        pcor_intermediate_project_model = self.pcor_project_model_from_code(project_code)
        key_dataset.project = pcor_intermediate_project_model

        json_string = self.produce_key_data_resource(key_dataset)
        logger.info("json_string: %s" % json_string)
        key_dataset_json = json.loads(json_string)
        status = self.submit_record(program=program_name, project=project_code, json_data=key_dataset_json)
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
        rendered = template.render(program=program).replace('"none"', 'null').replace('"None"', 'null').replace('""','null')
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
        rendered = template.render(model=project).replace('"none"', 'null').replace('"None"', 'null').replace('"nan"',
                                                                                                              'null').replace('""','null')
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
        rendered = template.render(resource=resource).replace('"none"', 'null').replace('"None"', 'null').replace('""','null').replace(
            'False', 'false').replace('True', 'true')
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
        rendered = template.render(discovery=discovery_data).replace('"none"', 'null').replace('"None"', 'null').replace('"nan"',
                                                                                                              'null').replace('""','null')
        return rendered

    def produce_geo_spatial_data_resource(self, geo_spatial_data_resource):
        """
        Render geo_spatial_data_resource  as JSON via template
        :param geo_spatial_data_resource: PcorGeospatialDataResourceModel representing the geo-spatial data
        :return: string with resource JSON for loading into Gen3
        """

        logger.info("produce_geo_spatial_data_resource()")
        template = self.env.get_template("geospatial_data_resource.jinja")
        rendered = template.render(geo_spatial_data_resource=geo_spatial_data_resource).replace('"none"', 'null') \
            .replace('"None"', 'null').replace('""','null').replace('False', 'false').replace('True', 'true').replace(u'\xa0', '') \
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
        rendered = template.render(geo_tool_resource=geo_spatial_tool_resource).replace('"none"', 'null') \
            .replace('"None"', 'null').replace('""','null').replace('False', 'false').replace('True', 'true')
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
        rendered = template.render(pop_data_resource=pop_data_resource).replace('"none"', 'null') \
            .replace('"None"', 'null').replace('""','null').replace('False', 'false').replace('True', 'true')
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_key_data_resource(self, key_data_resource):
        """
        Render key_data_resource  as JSON via template
        :param pop_data_resource: PcorPopDataResourceModel representing the population data
        :return: string with resource JSON for loading into Gen3
        """
        logger.info("produce_key_data_resource()")
        template = self.env.get_template("key_dataset_resource.jinja")
        rendered = template.render(key_data_resource=key_data_resource).replace('"none"', 'null') \
            .replace('"None"', 'null').replace('""','null').replace('False', 'false').replace('True', 'true')
        logger.info("rendered: %s" % rendered)
        return rendered


    #############################################
    # supporting methods
    ###########################################

    @staticmethod
    def check_tag_present(item, tags):
        for tag in tags:
            if item == tag.name:
                return True

        return False


    @staticmethod
    def check_program_exists(existing_programs, program):
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

    @staticmethod
    def check_discovery_entry_exists(existing_discovery_entries, new_entry):
        """
        checks if name/project.name in new_entry already exists we can expand validation in future if needed
        :param existing_discovery_entries:
            Dict{guid: {metadata}}: Dictionary with GUIDs as keys and associated
                metadata JSON blobs as values
        :param new_entry: metadata JSON blob
        :return:
            True if entry exist
            False if entry does not exist
        """
        logger.info("check_discovery_exists()")
        new_entry_name = new_entry['name']
        entry_already_exist = False
        existing_entry_guid = None
        if existing_discovery_entries:
            for entry_guid, existing_entry in existing_discovery_entries.items():
                temp_entry_name = existing_entry['gen3_discovery']['name']
                if temp_entry_name == new_entry_name:
                    entry_already_exist = True
                    existing_entry_guid = entry_guid
        return entry_already_exist, existing_entry_guid

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

    def pcor_project_model_from_code(self, project_submitter_id):
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
           name
           code
           short_name
           project_sponsor
           project_sponsor_type
           project_url
           dbgap_accession_number
         }}
       }}
       """.format(project_code)
        logger.info("query:{}".format(json))

        sub = Gen3Submission(self.gen3_auth)
        result = sub.query(query)
        logger.info("result:{}".format(result))

        if not result["data"]["project"]:
            raise Exception("Unable to get project '{}' from Gen3. Check User.yaml file".format(project_code))
        else:
            project = PcorIntermediateProjectModel()
            project.name = result["data"]["project"][0]["name"]
            project.short_name = result["data"]["project"][0]["short_name"]
            project.code = result["data"]["project"][0]["code"]
            project.sponsor = result["data"]["project"][0]["project_sponsor"]
            project.sponsor_type = result["data"]["project"][0]["project_sponsor_type"]
            project.project_url = result["data"]["project"][0]["project_url"]
            project.dbgap_accession_number = result["data"]["project"][0]["dbgap_accession_number"]
            project.id = result["data"]["project"][0]["id"]
            return project

    def get_discovery_entries(self):
        """
        Query all the discovery entries in 'discovery_metadata'
        :return:
            Dict{guid: {metadata}}: Dictionary with GUIDs as keys and associated
            metadata JSON blobs as values
        """
        logger.info('get_discovery_entries()')
        query = "data=True&_guid_type=discovery_metadata&limit=2000&offset=0"
        metadata = Gen3Metadata(self.gen3_auth)

        # for now limit is set to 100, add batch query for faster response
        response = metadata.query(query=query, return_full_metadata=True, limit=100)
        return response

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
            submission_status.project_code = project
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

            if submission_status.response_content.get("entities"):
                for entity in submission_status.response_content.get("entities"):
                    for error_entry in entity["errors"]:

                        error = PcorError()

                        if len(error_entry["keys"]) > 0:
                            error.key = error_entry["keys"][0]

                        error.message = error_entry["message"]
                        error.type = error_entry["type"]
                        submission_status.errors.append(error)

            if submission_status.response_content.get("message"):
                submission_status.message = submission_status.response_content.get("message")
            return submission_status

        except Exception as pcor_error:
            logger.error("error in submission:%s" % pcor_error)
            submission_status = PcorProcessResult()
            submission_status.success = False
            submission_status.program_name = program
            submission_status.project_code = project
            submission_status.request_content = pcor_error.request
            submission_status.response_content = json.loads(pcor_error.response.content)
            submission_status.traceback = traceback.format_exc()
            return submission_status

    def delete_nodes(self, program, project, ordered_node_list, batch_size=100, verbose=True):
        """
        Delete all records for a list of nodes from a project.

        :param program: The program to delete from.
        :param project: The project to delete from.
        :param ordered_node_list: The list of nodes to delete, in reverse graph submission order
        :param batch_size: how many records to query and delete at a time
        :param verbose: whether to print progress logs
        """
        logger.info("delete_nodes()")

        sub = Gen3Submission(self.gen3_auth)
        try:
            logger.info('\n\n\n\n===================Start deleting nodes====================================')
            sub.delete_nodes(program, project, ordered_node_list, batch_size, verbose)
            logger.info('\n===================Finished deleting nodes====================================\n\n\n\n')
        except Exception as pcor_error:
            logger.error("error in deletion:%s" % pcor_error)

    def resubmission_cleanups(self, program, project):
        """
        Clean up the existing project and records before re-submission
        :param program: identifier of the program in Gen3
        :param project: project name/code
        """
        logger.info('fetch project details')
        ordered_node_list = ['geospatial_data_resource', 'geospatial_tool_resource', 'population_data_resource',
                             'key_data_resource',
                             'resource']
        self.delete_nodes(program=program, project=project, ordered_node_list=ordered_node_list)
        self.delete_project(program=program, project_code=project)

    def cleanup_gen3_instance(self, program=None):
        """
        This is a helper function to cleanup gen3 instance
        It will delete all projects and records
        It will also delete all discovery metadata
        :param program: program name
        """
        logger.info('cleanup_gen3_instance()')

        # get all projects
        project_list = []
        existing_projects = self.get_projects(program=program)

        if existing_projects and 'links' in existing_projects:
            for entry in existing_projects['links']:
                temp_project = entry.split('/')[-1]
                project_list.append(temp_project)
        logger.info("project_list: %s" % project_list)

        # delete all projects and records
        for project in project_list:
            self.resubmission_cleanups(program=program, project=project)

        # delete all discovery metadata entries
        existing_discovery_entries = self.get_discovery_entries()
        for entry_guid in existing_discovery_entries:
            self.delete_discovery_metadata_with_guid(entry_guid)


