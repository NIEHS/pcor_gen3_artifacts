import json
import os
import logging
import pcor_testing_utilities


from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter

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
        project.project_name = "name"
        project.project_type ="type"
        project.project_state = "state"
        project.project_code = "code"
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
        os.chdir("..")
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
        resource.contact = "contact"
        resource.created_datetime = "2023/01/01T12:01:00Z"
        resource.keywords = ["this", "is", "keywords"]
        resource.license_text = "license text"
        resource.license_type = "license type"
        resource.name = "name"
        resource.secondary_name = "secondary name"
        resource.subject = "subject"
        resource.update_frequency = "frequency"
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
        discovery.type = "type1"
        discovery.subject = "subj1"
        discovery.resource_id = "rescid"
        discovery.description = "descr"
        discovery.full_name = "the full name"
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


    def test_add_project(self):
        """ Figure out how to clear and delete a project! """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        project = PcorIntermediateProjectModel()
        project.project_name = "NFS-2"
        project.project_code = "NFS-2"
        project.project_state = "open"
        project.project_release_date = "2023/01/01T12:01:00Z"
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = True
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.dbgap_accession_number = "NFS-2"
        project.date_collected = "2023/01/01T12:01:00Z"
        project.complete = "Complete"
        project.availability_type = "Open"
        pcor_ingest.create_project("NFS", project)

    def test_existing_delete_project(self):
        """ test delete project on existing project """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        # create project
        project.project_name = "test_delete_project"
        project.project_code = "test_delete_project"
        project.dbgap_accession_number = "test_delete_project"
        project.project_state = "open"
        project.project_release_date = "2023/01/01T12:01:00Z"
        project.support_source = "support source1"
        project.support_id = "support id1"
        project.releasable = True
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NIEHS"
        project.date_collected = "2023/01/01T12:01:00Z"
        project.complete = "Complete"
        project.availability_type = "Open"

        pcor_ingest.create_project(program=program, pcor_intermediate_project_model=project)
        response = pcor_ingest.delete_project(program=program, pcor_intermediate_project_model=project)
        self.assertTrue(response.status_code == 204)

    def test_non_existing_delete_project(self):
        """ test delete project on non existing project"""
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        project.project_name = "test_non_existing_project"
        expected = 'project does not exists'
        actual = pcor_ingest.delete_project(program=program, pcor_intermediate_project_model=project)
        self.assertEqual(expected, actual)

    def test_add_resource(self):
        """ Add a resource under a test project """
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        project.project_name = "NFS-2"
        project.project_code = "NFS-2"
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
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NFS-2-RESC-1"
        resource.resource_id = "NFS-2-RESC-1"
        resource.name = "Fire and Smoke Map"
        resource.resource_type = "data_resource"
        resource.subject = "AQI - Air Quality Index"
        resource.keywords = ["fire", "smoke", "aqi", "wildfire"]
        resource.update_frequency = "hourly"
        resource.secondary_name = "AirNow"
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "USFS - contact firesmokemap@epa.gov"
        resource.description = """The AirNow Fire and Smoke Map provides information that you can use to help protect your health from wildfire smoke. Use this map to see Current particle pollution air quality information for your location; Fire locations and smoke plumes; Smoke Forecast Outlooks, where available; and,Recommendations for actions to take to protect yourself from smoke. These recommendations were developed by EPA scientists who are experts in air quality and health. The Map is a collaborative effort between the U.S. Forest Service (USFS)-led Interagency Wildland Fire Air Quality Response Program and the U.S. Environmental Protection Agency (EPA)."""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        self.assertIsNotNone(actual)

    def test_parse_status(self):
        json = {"code": 200, "created_entity_count": 0, "entities": [{"action": "update", "errors": [], "id": "2c000697-43c0-442f-bb8f-10c6c6bf8ed6", "type": "resource", "unique_keys": [{"project_id": "NFS-NFS-2", "submitter_id": "NFS-2-RESC-1"}], "valid": True, "warnings": []}], "entity_error_count": 0, "message": "Transaction successful.","success": True, "transaction_id": 20, "transactional_error_count": 0, "transactional_errors": [], "updated_entity_count": 1}
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        actual = pcor_ingest.parse_status(json)
        self.assertEqual('NFS-2-RESC-1', actual.submitter_id)
        self.assertEqual('2c000697-43c0-442f-bb8f-10c6c6bf8ed6', actual.id)
        self.assertEqual('resource', actual.type)
        self.assertEqual('NFS-NFS-2', actual.project_id)