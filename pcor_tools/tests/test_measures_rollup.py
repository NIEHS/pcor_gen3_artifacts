import logging
import unittest

from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorGen3Ingest(unittest.TestCase):

    def test_measures_rollup_as_dataframe(self):
        logger.info('test_measures_rollup_as_dataframe()')

        measures_rollup = PcorMeasuresRollup(pcor_testing_utilities.get_pcor_ingest_configuration())

        df = measures_rollup.measures_rollup_as_dataframe()
        self.assertIsNotNone(df)

    def test_build_measures_structure(self):
        measures_rollup = PcorMeasuresRollup(pcor_testing_utilities.get_pcor_ingest_configuration())
        measures = measures_rollup.build_measures_structure()
        self.assertIsNotNone(measures)
        ehr = measures["Electronic Health Records"]
        self.assertEqual("Electronic Health Records", ehr.measure)
        self.assertEqual("Health", ehr.parent)
        self.assertEqual('Health Data', ehr.subcategory_major)

    def test_lookup_measure(self):
        measures_rollup = PcorMeasuresRollup(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_measure = "Womens Health"
        actual = measures_rollup.lookup_measure(test_measure)
        self.assertIsNotNone(actual)
        self.assertEqual(test_measure, actual.measure)

    def test_lookup_measure_other(self):
        measures_rollup = PcorMeasuresRollup(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_measure = "Notsmeasure"
        actual = measures_rollup.lookup_measure(test_measure)
        self.assertIsNotNone(actual)
        self.assertEqual(test_measure, actual.measure)
        self.assertEqual("Other", actual.parent)

    def test_process_measures(self):
        measures_rollup = PcorMeasuresRollup(pcor_testing_utilities.get_pcor_ingest_configuration())
        test_measure = ["Womens Health", "Nutrition", "Endocrine System", "Nutrition"]
        actual = measures_rollup.process_measures(test_measure)
        self.assertIsNotNone(actual)