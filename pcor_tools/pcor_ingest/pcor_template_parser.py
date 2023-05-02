import logging
import os
import pandas as pd

from pcor_ingest.pcor_intermediate_model import PcorProgramModel

logger = logging.getLogger(__name__)


class PcorTemplateParser:
    """
    A parent class for a parser of a PCOR spreadsheet template for a type
    """

    def __init__(self):
        pass

    def parse(self, template_absolute_path):

        # example path /deep/documents/foo.xls

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :return: PcorTemplateParseResult with the outcome
        """
        pass

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
        program = PcorProgramModel()
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'PROGRAM':
                logging.debug("found PROGRAM")
                for j in range(i, ss_rows):
                    if template_df.iat[j, 0] == 'program id':
                        program.dbgap_accession_number = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'program name':
                        program.name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'PROJECT':
                        return program

        logger.warn("no program found, return null")
        return None


class PcorTemplateParseResult:
    """
    Result of a parse action, indicates success or failure of parsing and any relevant error messages
    """

    def __init__(self, resource_type):

        """
        Init method for parse result
        :param resource_type: type of pcor resource parsed
        """
        self.errors=[]
        self.success=True
        self.model_data={}
        self.resource_type=None

