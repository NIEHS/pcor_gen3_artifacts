import json
import os
import logging

from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel,  PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorDataLoad(TestCase):
    """
    Loads sample data set for integration testing and demos
    """

    def test_add_sample_resources(self):
        """ Sample data load with discovery metadata """

      




