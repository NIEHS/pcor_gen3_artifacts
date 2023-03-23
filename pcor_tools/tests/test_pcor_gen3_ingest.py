import os
import logging
import pcor_testing_utilities


from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel


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

        self.assertIsNotNone(actual)
