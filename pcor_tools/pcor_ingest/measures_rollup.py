import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorIntermediateProgramModel, \
    PcorSubmissionInfoModel, MeasuresArrays

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PcorMeasuresRollupStructure:

    def __init__(self, parent, subcategory_major, subcategory_minor, measure):
        self.parent = parent
        self.subcategory_major = subcategory_major
        self.subcategory_minor = subcategory_minor
        self.measure = measure


class PcorMeasuresRollup:

    def __init__(self, pcor_ingest_configuration):
        """

        Parameters
        ----------
        pcor_ingest_configuration PcorIngestConfiguration that contains configuration from properties file
        """
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.measures = self.build_measures_structure()

    def measures_rollup_as_dataframe(self):
        """
        Get the data frame (pandas) from the measures spreadsheet

        Returns
        -------
        pandas.DataFrame representing the contents of the measures rollup

        """
        logger.info("measures_rollup_as_dataframe")
        df = pd.read_excel(self.pcor_ingest_configuration.measures_rollup, sheet_name='MeasuresFullView', engine='openpyxl')
        return df

    def build_measures_structure(self):

        """
        create a structure by measure that contains the rollup information

        Returns Dictionary with key of measure and value of PcorMeasuresRollup
        -------

        """

        logger.info("init_measures_structure()")
        df = self.measures_rollup_as_dataframe()
        measures_dict = {}

        ss_rows = df.shape[0]

        for i in range(ss_rows):
            if isinstance(df.iat[i, 4], str):
                measure = PcorMeasuresRollupStructure(PcorMeasuresRollup.filter_blank_measure(df.iat[i, 1]),
                                                      PcorMeasuresRollup.filter_blank_measure(df.iat[i, 2]),
                                                      PcorMeasuresRollup.filter_blank_measure(df.iat[i, 3]),
                                                      PcorMeasuresRollup.filter_blank_measure(df.iat[i, 4]))
                #logger.info("measure:%s" % measure)
                measures_dict[PcorMeasuresRollup.filter_blank_measure(df.iat[i, 4])] = measure

        return measures_dict

    @staticmethod
    def filter_blank_measure(measure):
        if isinstance(measure, str):
            return measure.title()
        else:
            return "Other"

    def lookup_measure(self, measure):
        """
        For a given measure, return the rollup
        Parameters
        ----------
        measure - str with the measure

        Returns PcorMeasuresRollupStructure associated with the measure
        -------
        """

        rollup = self.measures.get(measure.title())

        if rollup:
            return rollup
        else:
            return PcorMeasuresRollupStructure("Other", "Other", "Other", measure)

    def process_measures(self, measures):
        """
        for an array of measures, return three arrays which are the measures rollup for each
        of the provided measures with duplicates filtered

        Parameters
        ----------
        measures - str[] with the measures

        Returns MeasuresArrays with the complete rollup of each measure
        -------
        """

        measures_arrays = MeasuresArrays()

        for measure in measures:

            if measure not in measures_arrays.measures:
                measures_arrays.measures.append(measure.title())
                measure_rollup = self.lookup_measure(measure)

                if measure_rollup.parent not in measures_arrays.measures_parents:
                    measures_arrays.measures_parents.append(measure_rollup.parent)

                if measure_rollup.subcategory_major not in measures_arrays.measures_subcategories_major:
                    measures_arrays.measures_subcategories_major.append(measure_rollup.subcategory_major)

                if measure_rollup.subcategory_minor not in measures_arrays.measures_subcategories_minor:
                    measures_arrays.measures_subcategories_minor.append(measure_rollup.subcategory_minor)

        return measures_arrays
