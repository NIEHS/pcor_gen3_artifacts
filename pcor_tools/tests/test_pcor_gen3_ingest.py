import logging
import unittest

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorGen3Ingest(unittest.TestCase):

    def test_delete_project(self):
        """ test delete project on existing project """
        logger.info('test_delete_project()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "CHORDS"
        project = PcorIntermediateProjectModel()
        project.code = "MODIS"

        pcor_ingest.delete_project(program=program, project_code=project.code)

    def test_delete_discovery_metadata_with_guid(self):
        # not a real test used to delete discovery entry
        logger.info('test_delete_discovery_metadata_with_guid()')

        guid = 'ec97f67f-ec59-4859-bdf9-9343122f80cb'  # hardcode entry to be deleted

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        actual = pcor_ingest.delete_discovery_metadata_with_guid(guid=guid)
        logger.info(actual)

    def test_check_discovery_exists(self):
        logger.info('test_check_discovery_exists()')
        new_entry = {
            "program_name": "CHORDS",
            "program_type": "",
            "program_url": "",
            "project_name": "EPA-AQS",
            "project_type": "",
            "project_url": "",
            "project_description": "EPA plays a crucial role in monitoring and maintaining air quality in the US. The EPA's Air Quality System (AQS) is a comprehensive network of monitoring stations that collect data on various air pollutants (Lamsal et al., 2008).",
            "name": "EPA-AQS",
            "short_name": "",
            "verification_datetime": "",
            "payment_required": "",
            "investigator_name": "",
            "investigator_affiliation": "",
            "comment": "",
            "short_name": "",
            "description": "EPA’s monitoring stations provide hourly measurements of pollutants such as nitrogen dioxide (NO2), ozone (O3), and particulate matter (PM) (Lamsal et al., 2008). The data collected by the AQS is considered the \"gold standard\" for measuring air pollutants (Considine et al., 2023). The EPA's efforts to improve air quality are guided by the Clean Air Act, which requires the agency to evaluate the costs and benefits of new rules and regulations (McGuffey, 2016).",
            "support_source": "",
            "source_url": "",
            "citation": "",
            "resource_id": "80468b14-c227-4d2d-a3c1-7f3e8bdf298f",
            "resource_url": "www.epa.gov/aqs",
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
