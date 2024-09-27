import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorIntermediateProgramModel, \
    PcorSubmissionInfoModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarResourceParser:
    """
    A parent class for a parser of a PCOR Cedar for a type
    """

    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest = PcorGen3Ingest(pcor_ingest_configuration)
        self.pcor_measures_rollup = PcorMeasuresRollup(pcor_ingest_configuration)
        self.yyyy_pattern = r"\b(\d{4})\b"

    def parse(self, template_absolute_path, result):

        # example path /deep/documents/foo.xls
        logger.info("parse()")

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :param result: PcorTemplateParseResult with the outcome
        """
        warnings.simplefilter(action='ignore', category=UserWarning)
        with open(template_absolute_path, 'r') as f:
            contents_json = json.loads(f.read())

        try:
            result.model_data["submission"] = self.extract_submission_data(contents_json)
        except Exception as err:
            logger.error("exception parsing submission: %s" % str(err))
            result.success = False
            result.errors.append("error parsing submission: %s" % str(err))
            result.traceback = traceback.format_exc()
            result.message = str(err)
            return

        try:

            program = self.extract_program_data(contents_json)
            result.model_data["program"] = program
            result.program_name = program.name

        except Exception as err:
            logger.error("exception parsing program: %s" % str(err))
            result.success = False
            result.errors.append("error parsing program: %s" % str(err))
            result.traceback = traceback.format_exc()
            result.message = str(err)
            return

        try:
            project = self.extract_project_data(contents_json)
            result.model_data["project"] = project
            result.project_guid = project.submitter_id
            result.project_code = project.code
        except Exception as err:
            logger.error("exception parsing project: %s" % str(err))
            result.success = False
            result.errors.append("error parsing project: %s" % str(err))
            result.message = str(err)
            result.traceback = traceback.format_exc()
            return

        result.project_name = result.model_data["project"].name

        try:
            resource = self.extract_resource_data(contents_json)
            result.model_data["resource"] = resource
            result.resource_guid = resource.submitter_id
            result.resource_name = resource.name
        except Exception as err:
            logger.error("exception parsing resource: %s" % str(err))
            result.success = False
            result.errors.append("error parsing resource: %s" % str(err))
            result.message = str(err)
            result.traceback = traceback.format_exc()

    @staticmethod
    def extract_program_data(template_df):
        """
        Given a pandas dataframe with the template date, extract out the program related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProgramModel with program data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the PROGRAM stanza")
        program = PcorIntermediateProgramModel()
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Program':
                logging.debug("found Program")
                for j in range(i, ss_rows):
                    # FixMe:  program id is missing in template!
                    if template_df.iat[j, 0] == 'program id':
                        program.dbgap_accession_number = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'program_name':
                        program.name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'Project':
                        # validate needed props
                        # ToDo: what is assignment logic?
                        if program.dbgap_accession_number == "" or program.dbgap_accession_number is None:
                            program.dbgap_accession_number = program.name
                        return program

        logger.warning("no program found, return null")
        return None