import logging
import unittest

import pandas as pd

from pcor_ingest.geospatial_data_resource_parser import GeoSpatialDataResourceParser
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorGeospatialDataResourceModel, \
    PcorIntermediateProgramModel
from pcor_ingest.pcor_template_process_result import PcorProcessResult
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorTemplateParser(unittest.TestCase):

    def test_parse_publications(self):
        test_ss_path = './test_resources/GioExposure_1.4.1_ColoradoPM2.5.xlsm'
        parser = GeoSpatialDataResourceParser()
        result = PcorProcessResult()
        actual = parser.parse(test_ss_path, result)
        logger.info("parsed data: %s" % result)
        self.assertIsNotNone(result)
        discovery = PcorGen3Ingest.create_discovery_from_resource(PcorIntermediateProgramModel(), PcorIntermediateProjectModel(), result.model_data["resource"], PcorGeospatialDataResourceModel())

        logger.info("discovery %s", discovery)
