import json
import os
import logging

from unittest import TestCase
import requests

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorGen3Ingest(TestCase):
    """
    Testing of pcor ingest, most tests require standup of the pcor docker-compose framework
    """
    def test_produce_project_json(self):
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        project = PcorIntermediateProjectModel()
        project.name = "name"
        project.short_name = "short name"
        project.project_type = "type"
        project.project_state = "state"
        project.code = "code"
        project.availability_mechanism = "availability_mechanism"
        project.availability_type = "availability_type"
        project.complete = True
        project.date_collected = "2023/01/01T12:00:00Z"
        project.dbgap_accession_number = "dbgap_accession_number"
        project.id = "id"
        project.investigator_affiliation = "investigator_affiliation"
        project.investigator_name = "investigator_name"
        project.project_release_date = "023/01/01T12:00:00Z"
        project.releasable = True
        project.support_id = "support_id"
        project.support_source = "support_source"
        project.project_type = "Data Provider"
        project.project_url = "http://project.url"
        actual = pcor_ingest.produce_project_json(project)
        json.loads(actual)

    def test_produce_resource_json(self):
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        project = PcorIntermediateProjectModel()
        resource = PcorIntermediateResourceModel()
        project.id = "id"
        project.submitter_id = "submitter_id"
        resource.project = project
        resource.submitter_id = "resc submitter_id"
        resource.resource_type = "resc type"
        resource.description = "description"
        resource.citation = "citation"
        resource.resource_contact = "contact"
        resource.resource_link = "http://resource.link"
        resource.created_datetime = "2023/01/01T12:01:00Z"
        resource.verification_datetime = "2023/01/01T12:01:00Z"
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.name = "name"
        resource.short_name = "secondary name"
        resource.payment_required = "false"
        resource.domain = ["subject"]
        resource.resource_use_agreement = "false"
        actual = pcor_ingest.produce_resource_json(resource)
        json.loads(actual)

    def test_produce_discovery_json(self):
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "tag1"
        tag.category = "cat1"
        discovery.tags.append(tag)

        discovery.name = "name1"
        discovery.investigator_name = "inv name"
        discovery.investigator_affiliation = "inv affil"
        discovery.intended_use = "intended use"
        discovery.full_name = "the full name"
        discovery.description = "descr"
        discovery.support_source = "support source"
        discovery.source_url = "http://source.url"
        discovery.citation = "citation"
        discovery.type = "type1"
        discovery.domain = "subj1"
        discovery.has_api = "false"
        discovery.is_citizen_collected = "false"
        discovery.license_type = "license_type"
        discovery.license_text = "license_text"
        discovery.resource_use_agreement = "true"
        discovery.resource_contact = "contact"

        discovery.resource_id = "rescid"
        discovery.resource_url = "http://hello.com"

        adv_search_filter = AdvSearchFilter()
        adv_search_filter.key = "adv_key1"
        adv_search_filter.value = "adv_val1"
        discovery.adv_search_filters.append(adv_search_filter)
        adv_search_filter = AdvSearchFilter()
        adv_search_filter.key = "adv_key2"
        adv_search_filter.value = "adv_val2"
        discovery.adv_search_filters.append(adv_search_filter)
        actual = pcor_ingest.produce_discovery_json(discovery)
        json.loads(actual)

    def test_add_program(self):
        """ Figure out how to clear and delete a program! """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        program_id = pcor_ingest.create_program(program)
        self.assertIsNotNone(program_id, 'no program id returned')

    def test_add_project(self):
        """ Figure out how to clear and delete a project! """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.short_name = "NFS-2"
        project.code = "NFS-2"
        project.project_type = "Data Provider"
        project.project_url = "https://www.niehs.nih.gov"
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = "2023/01/01T12:01:00Z"
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)

    def test_existing_delete_project(self):
        """ test delete project on existing project """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.short_name = "NFS-2"
        project.code = "NFS-2"
        project.project_type = "Data Provider"
        project.project_url = "https://www.niehs.nih.gov"
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = "2023/01/01T12:01:00Z"
        project.complete = "Complete"
        project.availability_type = "Open"

        pcor_ingest.create_project(program=program, pcor_intermediate_project_model=project)
        pcor_ingest.delete_project(program=program, project_name=project.name)

    def test_non_existing_delete_project(self):
        """ test delete project on non existing project"""
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        project_name = "test_non_existing_project"
        expected = 'project does not exist'
        try:
            actual = pcor_ingest.delete_project(program=program, project_name=project_name)
        except requests.exceptions.HTTPError:
            logger.warn("error, project not found")
            return

    def test_add_resource(self):
        """ Add a resource under a test project """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        program_id = pcor_ingest.create_program(program)


        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.short_name = "NFS-2"
        project.code = "NFS-2"
        project.project_type = "Data Provider"
        project.project_url = "https://www.niehs.nih.gov"
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = "2023/01/01T12:01:00Z"
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)
        project.id = project_id
        logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))
        pcor_ingest.create_project(program=program.dbgap_accession_number, pcor_intermediate_project_model=project)

        resource = PcorIntermediateResourceModel()
        resource.project = project
        resource.submitter_id = "resc submitter_id"
        resource.resource_type = "data_resource"
        resource.description = "description"
        resource.citation = "citation"
        resource.resource_contact = "contact"
        resource.resource_link = "http://resource.link"
        resource.created_datetime = "2023/01/01T12:01:00Z"
        resource.verification_datetime = "2023/01/01T12:01:00Z"
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.name = "name"
        resource.short_name = "secondary name"
        resource.payment_required = "false"
        resource.domain = ["subject"]
        resource.resource_use_agreement = "false"
        actual = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)
        self.assertIsNotNone(actual)

    def test_decorate_resource(self):
        """ Add a resource under a test project and decorate with discovery metadata """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        program_id = pcor_ingest.create_program(program)

        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.short_name = "NFS-2"
        project.code = "NFS-2"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = "true"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)
        logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NFS-2-RESC-DISC-1"
        resource.resource_id = "NFS-2-RESC-DISC-1"
        resource.name = "Fire and Smoke Map"
        resource.short_name = "short name"
        resource.resource_type = "data_resource"
        resource.description = "description"
        resource.intended_use = "intended use"
        resource.citation = "citation"
        resource.is_citizen_collected = "false"
        resource.has_api = "false"
        resource.domain = ["AQI - Air Quality Index"]
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.name = "name"
        resource.short_name = "secondary name"
        resource.payment_required = "false"
        resource.domain = ["subject"]
        resource.resource_use_agreement = "false"
        resc_id = resource.id

        # now add the discovery data
        discovery = pcor_ingest.create_discovery_from_resource(program.name, project, resource)

        tag = Tag()
        tag.name = "NFS"
        tag.category = "Program"
        discovery.tags.append(tag)

        actual = pcor_ingest.decorate_resc_with_discovery(discovery)
        self.assertIsNotNone(actual)

    def test_create_geo_spatial_data_resource(self):
        """ Add a geo_spatial_data_resource """

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        program_id = pcor_ingest.create_program(program)

        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.short_name = "NFS-2"
        project.code = "NFS-2"
        project.project_state = "open"
        project.project_type = "Data Provider"
        project.project_release_date = ""
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = "true"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)
        logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NFS-2-RESC-1"
        resource.resource_id = "NFS-2-RESC-1"
        resource.name = "Fire and Smoke Map"
        resource.short_name = "short name"
        resource.resource_type = "data_resource"
        resource.description = "description"
        resource.citation = "citation"
        resource.is_citizen_collected = "false"
        resource.has_api = "false"
        resource.domain = ["AQI - Air Quality Index"]
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.payment_required = "false"
        resource.domain = ["subject"]
        resource.resource_use_agreement = "false"
        resource.resource_link = "https://landfire.gov/"
        resource_submit_status = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)

        geo_spatial_resource = PcorGeospatialDataResourceModel()
        geo_spatial_resource.submitter_id = "NFS-2-GEO-1"
        geo_spatial_resource.comments = "comment"
        geo_spatial_resource.intended_use = "intended use" # TODO: do we need a second general comment field in discovery? mc
        geo_spatial_resource.resource_submitter_id = resource.submitter_id
        geo_spatial_resource.update_frequency = "unknown"
        geo_spatial_resource.includes_citizen_collected = "false"
        geo_spatial_resource.has_api = "false"
        geo_spatial_resource.has_visualization_tool = "false"
        geo_spatial_resource.measures = ["measure1", "measure2"]
        geo_spatial_resource.measurement_method = "method1"
        geo_spatial_resource.spatial_coverage = "national"
        geo_spatial_resource.spatial_resolution = "10km"
        geo_spatial_resource.temporal_resolution = "unknown"

        # using result from resource creation status
        geo_spatial_resource.resource_id = resource_submit_status.id
        geo_spatial_resource.project_submitter_id = resource.submitter_id

        actual = pcor_ingest.create_geo_spatial_data_resource(program_name=program.name,
                                                              project_name=project.name,
                                                              geo_spatial_data_resource=geo_spatial_resource)

        # now decorate with metadata

        discovery_data = pcor_ingest.create_discovery_from_resource(program.name, project, resource)
        discovery_data.comment = geo_spatial_resource.comments # intended use?
        pcor_ingest.decorate_resc_with_discovery(discovery_data)

    def test_create_geo_spatial_tool_resource(self):
        """ Add a geo_spatial_tool_resource """

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NOAA'
        program.dbgap_accession_number = 'NOAA'
        program_id = pcor_ingest.create_program(program)

        project = PcorIntermediateProjectModel()
        project.name = "NOAA-1"
        project.short_name = "NOAA-1"
        project.code = "NOAA-1"
        project.project_state = "open"
        project.project_type = "Data Provider"
        project.project_release_date = ""
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = "true"
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NOAA-1"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project(program.name, project)
        logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NOAA-1-RESC-3"
        resource.resource_id = "NOAA-1-RESC-3"
        resource.name = "geo tool 1"
        resource.short_name = "geotool1"
        resource.resource_type = "tool_resource"
        resource.description = "description"
        resource.citation = "citation"
        resource.is_citizen_collected = "false"
        resource.has_api = "false"
        resource.domain = ["AQI - Air Quality Index"]
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.payment_required = "false"
        resource.domain = ["subject"]
        resource.resource_use_agreement = "false"
        resource.resource_link = "https://landfire.gov/"
        resource_submit_status = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)

        geo_tool_resource = PcorGeoToolModel()
        geo_tool_resource.submitter_id = "NOAA-1-GEOTOOL-1"
        geo_tool_resource.resource_submitter_id = resource.submitter_id
        geo_tool_resource.spatial_coverage = "national"
        geo_tool_resource.spatial_resolution = "10km"
        geo_tool_resource.temporal_resolution = "unknown"
        geo_tool_resource.is_open_source = "false"
        geo_tool_resource.tool_type = ["software"]
        geo_tool_resource.usage_type = "Open-source"
        geo_tool_resource.operating_system.append("Linux")
        geo_tool_resource.languages.append("Go")
        geo_tool_resource.input_formats.append("Net/CDF")
        geo_tool_resource.output_formats.append("binary")

        # using result from resource creation status
        geo_tool_resource.resource_id = resource_submit_status.id
        geo_tool_resource.project_submitter_id = resource.submitter_id

        actual = pcor_ingest.create_geo_spatial_tool_resource(program_name=program.name,
                                                              project_name=project.name,
                                                              geo_spatial_tool_resource=geo_tool_resource)

        # now decorate with metadata

        discovery_data = pcor_ingest.create_discovery_from_resource(program.name, project, resource)
        pcor_ingest.decorate_resc_with_discovery(discovery_data)

    def test_create_pop_data_resource(self):
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        program_id = pcor_ingest.create_program(program)

        project = PcorIntermediateProjectModel()
        project.name = "NFS-2"
        project.code = "NFS-2"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = True
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)
        logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NFS-2-RESC-1"
        resource.resource_id = "NFS-2-RESC-1"
        resource.name = "Population Map"
        resource.resource_type = "data_resource"
        resource.subject = "Urban/Wild Interface"
        resource.keywords = ["urban/wild interface", "demographic", "wildfire"]
        resource.update_frequency = "hourly"
        resource.secondary_name = "A map"
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "USFS - contact firesmokemap@epa.gov"
        resource.description = """The AirNow Fire and Smoke Map provides information that you can use to help protect your health from wildfire smoke. Use this map to see Current particle pollution air quality information for your location; Fire locations and smoke plumes; Smoke Forecast Outlooks, where available; and,Recommendations for actions to take to protect yourself from smoke. These recommendations were developed by EPA scientists who are experts in air quality and health. The Map is a collaborative effort between the U.S. Forest Service (USFS)-led Interagency Wildland Fire Air Quality Response Program and the U.S. Environmental Protection Agency (EPA)."""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        resource_submit_status = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)

        pop_data_resource = PcorPopDataResourceModel()
        pop_data_resource.submitter_id = "NFS-2-POP-1"
        pop_data_resource.spatial_coverage = "national"
        pop_data_resource.spatial_resolution = "10km"
        pop_data_resource.population = ["wildland/urban interface"]
        pop_data_resource.exposures.append("toxic smoke")
        pop_data_resource.outcomes.append("asthma")
        pop_data_resource.resource_link = "https://landfire.gov/"

        # using result from resource creation status
        pop_data_resource.resource_id = resource_submit_status.id
        pop_data_resource.resource_submitter_id = resource.submitter_id

        actual = pcor_ingest.create_pop_data_resource(program_name=program.name,
                                                      project_name=project.name,
                                                      pop_data_resource=pop_data_resource)

        # now decorate with metadata

        discovery_data = pcor_ingest.create_discovery_from_resource(program.name, project, resource)
        pcor_ingest.decorate_resc_with_discovery(discovery_data)


    def test_parse_status(self):
        json = {"code": 200, "created_entity_count": 0, "entities": [{"action": "update", "errors": [], "id": "2c000697-43c0-442f-bb8f-10c6c6bf8ed6", "type": "resource", "unique_keys": [{"project_id": "NFS-NFS-2", "submitter_id": "NFS-2-RESC-1"}], "valid": True, "warnings": []}], "entity_error_count": 0, "message": "Transaction successful.","success": True, "transaction_id": 20, "transactional_error_count": 0, "transactional_errors": [], "updated_entity_count": 1}
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        actual = pcor_ingest.parse_status(json)
        self.assertEqual('NFS-2-RESC-1', actual.submitter_id)
        self.assertEqual('2c000697-43c0-442f-bb8f-10c6c6bf8ed6', actual.id)
        self.assertEqual('resource', actual.type)
        self.assertEqual('NFS-NFS-2', actual.project_id)
