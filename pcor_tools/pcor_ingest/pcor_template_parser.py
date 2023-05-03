import logging
import os
import pandas as pd

from pcor_ingest.pcor_intermediate_model import PcorProgramModel, PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorGeospatialDataResourceModel

logger = logging.getLogger(__name__)


class PcorTemplateParser:
    """
    A parent class for a parser of a PCOR spreadsheet template for a type
    """

    def __init__(self):
        pass

    def parse(self, template_absolute_path):

        # example path /deep/documents/foo.xls
        logger.info("parse()")

        """
        Parse a spreadsheet template for a file at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :return: PcorTemplateParseResult with the outcome
        """
        parse_result = PcorTemplateParseResult()
        df = pd.read_excel(template_absolute_path, sheet_name=0)

        try:
            parse_result.model_data["program"] = self.extract_program_data(df)
        except Exception as err:
            logger.error("exception parsing program: %s" % err)
            parse_result.success = False
            parse_result.errors.append("error parsing program: %s" % err)
            return parse_result

        try:
            parse_result.model_data["project"] = self.extract_project_data(df)
        except Exception as err:
            logger.error("exception parsing project: %s" % err)
            parse_result.success = False
            parse_result.errors.append("error parsing project: %s" % err)
            return parse_result

        try:
            parse_result.model_data["resource"] = self.extract_resource_data(df)
        except Exception as err:
            logger.error("exception parsing resource: %s" % err)
            parse_result.success = False
            parse_result.errors.append("error parsing resource: %s" % err)
            return parse_result

        logger.info("returning general parsed data: %s" % parse_result)
        return parse_result


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

    @staticmethod
    def extract_project_data(template_df):
        """
        Given a pandas dataframe with the template date, extract out the project related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the PROJECT stanza")
        project = PcorIntermediateProjectModel()
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'PROJECT':
                logging.debug("found PROJECT")
                for j in range(i, ss_rows):
                    if template_df.iat[j, 0] == 'submitter id':
                        project.submitter_id = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'availability type':
                        project.availability_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'RESOURCE':
                        return project

        logger.warn("no program found, return null")
        return None

    @staticmethod
    def extract_resource_data(template_df):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the RESOURCE stanza")
        resource = PcorIntermediateResourceModel()

        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'RESOURCE':
                logging.debug("found RESOURCE")
                for j in range(i, ss_rows):
                    if template_df.iat[j, 0] == 'submitter id':
                        resource.submitter_id = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'source url':
                        resource.source_url = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'source name':
                        resource.source_name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'RESOURCE DETAILS':
                        return resource

        logger.warn("no program found, return null")
        return None


class PcorTemplateParseResult:
    """
    Result of a parse action, indicates success or failure of parsing and any relevant error messages
    """

    def __init__(self):

        """
        Init method for parse result
        """
        self.errors=[]
        self.success=True
        self.model_data={}
        self.resource_type=None

