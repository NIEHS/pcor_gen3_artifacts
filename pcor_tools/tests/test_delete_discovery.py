import logging
import unittest

from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestDeleteDiscovery(unittest.TestCase):

    def test_delete_discovery_metadata_with_guid(self):
        logger.info('test_delete_discovery_metadata_with_guid()')

        guid = 'b8058b19-46bd-4f7a-bca9-edd30e35c314'   # hardcode entry to be deleted

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        actual = pcor_ingest.delete_discovery_metadata_with_guid(guid=guid)
        logger.info(actual)
