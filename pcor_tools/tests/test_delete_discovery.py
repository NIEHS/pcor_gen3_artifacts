import unittest

import json
import os
import logging

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_template_process_result import PcorProcessResult
from pcor_ingest.spreadsheet_reader import PcorSpreadsheeetReader
from tests import pcor_testing_utilities
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestDeleteDiscovery(unittest.TestCase):

    def test_delete_discovery_metadata_with_guid(self):
        logger.info('test_delete_discovery_metadata_with_guid()')
        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        guid = 'c5ee5429-46ec-42de-9cc3-aca22e71c37b'

        actual = pcor_ingest.delete_discovery_metadata_with_guid(guid=guid)
        logger.info(actual)
