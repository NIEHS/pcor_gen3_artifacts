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
    PcorSubmissionInfoModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PcorMeasuresRollupStructure:

    def __init__(self, parent, subcategory, measure):
        self.parent = parent
        self.subcategory = subcategory
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
        df = pd.read_excel(self.pcor_ingest_configuration.measures_rollup, sheet_name='MeasureList', engine='openpyxl')
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
            if isinstance(df.iat[i, 0], str):
                measure = PcorMeasuresRollupStructure(df.iat[i, 0], df.iat[i, 1], df.iat[i, 2])
                logger.info("measure:%s" % measure)
                measures_dict[df.iat[i, 2]] = measure

        return measures_dict

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
            return PcorMeasuresRollupStructure("Other", "Other", measure)
