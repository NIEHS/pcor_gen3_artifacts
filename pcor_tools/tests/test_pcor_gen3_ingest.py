import json
import os
import logging
import pcor_testing_utilities


from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel

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
        #os.chdir("..")
        actual = pcor_ingest.produce_resource_json(resource)
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
