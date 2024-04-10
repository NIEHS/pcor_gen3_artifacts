import logging
import unittest
import uuid

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorGen3Ingest(unittest.TestCase):
    def test_create_program(self):
        logger.info('test_create_program()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = {
            "type": "program",
            "name": "TestProgram",
            "dbgap_accession_number": "TestProgram",
        }
        program_id = pcor_ingest.create_program(program=program)
        try:
            uuid.UUID(program_id, version=4)
        except ValueError:
            self.fail(f"Return value {program_id} is not a valid UUID")

    def test_delete_program(self):
        logger.info('test_delete_program()')
        self.test_create_program()
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "TestProgram"
        response = pcor_ingest.delete_program(program=program)
        assert response.status_code == 204

    def test_get_projects(self):
        logger.info('test_get_projects()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "TestProgram"
        actual = pcor_ingest.get_projects(program=program)
        logger.info(actual)

    def test_create_project(self):
        logger.info('test_create_project()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "TestProgram"
        project = PcorIntermediateProjectModel()
        project.code = "MTBS"
        project.name = "MTBS"
        project.dbgap_accession_number = "test-db-gap-accession-number"
        project.description = "test project description"
        project.program = program
        project_id = pcor_ingest.create_project(program=program, pcor_intermediate_project_model=project)
        try:
            uuid.UUID(project_id, version=4)
        except ValueError:
            self.fail(f"Return value {project_id} is not a valid UUID")

    def test_delete_project(self):
        """ test delete project on existing project """
        logger.info('test_delete_project()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "TestProgram"
        project = PcorIntermediateProjectModel()
        project.code = "MTBS"
        response = pcor_ingest.delete_project(program=program, project_code=project.code)
        assert response.status_code == 204

    def test_delete_nodes(self):
        """ test delete nodes on existing project """
        logger.info('test_delete_nodes()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "TestProgram"
        project = PcorIntermediateProjectModel()
        project.code = "MTBS"
        ordered_node_list = ['geospatial_data_resource', 'geospatial_tool_resource', 'population_data_resource',
                             'resource']

        pcor_ingest.delete_nodes(program=program, project=project.code, ordered_node_list=ordered_node_list)

    def test_delete_discovery_metadata_with_guid(self):
        # not a real test used to delete discovery entry
        logger.info('test_delete_discovery_metadata_with_guid()')

        guid = 'b98b3e30-9ae7-4d6b-97fd-d501de46ea04'  # hardcode entry to be deleted

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        actual = pcor_ingest.delete_discovery_metadata_with_guid(guid=guid)
        logger.info(actual)

    def test_check_discovery_exists(self):
        logger.info('test_check_discovery_exists()')
        new_entry = {
            "program_name": "TestProgram",
            "program_type": "",
            "program_url": "",
            "project_name": "test-project",
            "project_type": "",
            "project_url": "",
            "project_description": "test project description",
            "name": "MTBS",
            "short_name": "",
            "verification_datetime": "",
            "payment_required": "",
            "investigator_name": "",
            "investigator_affiliation": "",
            "comment": "",
            "description": "test resource description",
            "support_source": "",
            "source_url": "",
            "citation": "",
            "resource_id": "80468b14-c227-4d2d-a3c1-7f3e8bdf298f",
            "resource_url": "www.dummy-test-link.com/test",
            "type": "GeoExposureData",
            "domain": "Air Quality",
            "has_api": "True",
            "has_visualization_tool": "True",
            "is_citizen_collected": "False",
            "license_type": "",
            "license_text": "",
            "resource_use_agreement": "None",
            "resource_contact": ""
        }

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_query = "data=True&_guid_type=discovery_metadata&limit=2000&offset=0"

        existing_discovery_entires = pcor_ingest.get_discovery_entries()
        response = pcor_ingest.check_discovery_entry_exists(existing_discovery_entries=existing_discovery_entires,
                                                            new_entry=new_entry)
        logger.info(response)

    def test_cleanup_gen3_instance(self):
        """
        This is a helper function to cleanup gen3 instance
        It will delete all projects and records
        It will also delete all discovery metadata
        """
        logger.info('cleanup_gen3_instance()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "CHORDS"
        pcor_ingest.cleanup_gen3_instance(program=program)
