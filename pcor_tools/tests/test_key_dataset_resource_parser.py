import logging
import unittest

from pcor_ingest.key_dataset_resource_parser import KeyDatasetResourceParser
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestKeyDatasetResourceParser(unittest.TestCase):

    def test_parse(self):
        test_ss_path = 'test_resources/key-datasets-sample-1.2.xlsx'
        actual = []
        parser = KeyDatasetResourceParser(pcor_testing_utilities.get_pcor_ingest_configuration())
        parser.parse(test_ss_path, actual)
        logger.info("parse_result: %s" % actual)
        self.assertIsNotNone(actual)

    def test_parse_pubs(self):
        pubs = "Global Modeling and Assimilation Office (GMAO) (2015), MERRA-2 inst3_3d_aer_Nv: 3d, 3-Hourly, Instantaneous, Model-Level, Assimilation, Aerosol Mixing Ratio V5.12.4, Greenbelt, MD, USA, Goddard Earth Sciences Data and Information Services Center (GES DISC), [Accessed: https://doi.org/10.5067/LTVB4GPCOTK2]; Gelaro, R., McCarty, W., Suárez, M. J., Todling, R., Molod, A., Takacs, L., ... & Zhao, B. (2017). The modern-era retrospective analysis for research and applications, version 2 (MERRA-2). Journal of climate, 30(14), 5419-5454."
        actual = KeyDatasetResourceParser.make_complex_array_from_pubs(pubs)
        self.assertEqual(2, len(actual))


if __name__ == '__main__':
    unittest.main()