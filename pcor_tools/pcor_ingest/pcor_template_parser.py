import logging
import os
import pandas as pd

from pcor_ingest.pcor_intermediate_model import PcorProgramModel, PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorGeospatialDataResourceModel, PcorIntermediateProgramModel

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
                    elif template_df.iat[j, 0] == 'program_long_name':
                        program.long_name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'program_type':
                        program.program_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'program_url':
                        program.program_url = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'program_description':
                        program.program_description = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'Project':

                        # ToDo: dbgap_accession_number assignment logic?
                        if program.dbgap_accession_number == "" or program.dbgap_accession_number is None:
                            program.dbgap_accession_number = program.name
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
            if template_df.iat[i, 0] == 'Project':
                logging.debug("found Project")
                for j in range(i, ss_rows):
                    # FixMe:  submitter id is missing in template!
                    if template_df.iat[j, 0] == 'submitter id':
                        project.submitter_id = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'project_name':
                        project.name = template_df.iat[j, 1]
                    # FixMe:  code is missing in template!
                    elif template_df.iat[j, 0] == 'code':
                        project.code = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'project_long_name':
                        project.long_names = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'project_type':
                        project.project_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'project_url':
                        project.project_url = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'project_description':
                        project.description = template_df.iat[j, 1]

                    # FixMe:  following things are missing in template!
                    elif template_df.iat[j, 0] == 'date collected':
                        project.date_collected = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'complete':
                        project.complete = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'availability type':
                        project.availability_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'Resource':

                        # ToDo: code and dbgap_accession_number assignment logic?
                        if project.code == "" or project.code is None:
                            project.code = project.name
                        if project.dbgap_accession_number == "" or project.dbgap_accession_number is None:
                            project.dbgap_accession_number = project.name
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
        logging.debug("iterate looking for the Resource stanza")
        resource = PcorIntermediateResourceModel()

        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Resource':
                logging.debug("found Resource")
                for j in range(i, ss_rows):
                    # FixMe:  submitter id is missing in template!
                    if template_df.iat[j, 0] == 'submitter id':
                        resource.submitter_id = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_name':
                        resource.source_name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_short_name':
                        resource.short_name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_type':
                        resource.resource_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_url':
                        resource.source_url = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_description':
                        resource.description = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'domain':
                        resource.domain = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'keywords':
                        resource.keywords = template_df.iat[j, 1]

                    # FixMe:  access_type is missing in schema!
                    elif template_df.iat[j, 0] == 'access_type':
                        resource.access_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'payment_required':
                        resource.payment_required = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'date_added':
                        resource.created_datetime = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'date_updated':
                        resource.updated_datetime = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'date_verified':
                        resource.verification_datetime = template_df.iat[j, 1]

                    # FixMe:  resource_reference is missing in schema!
                    elif template_df.iat[j, 0] == 'resource_reference':
                        resource.resource_reference = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'resource_use_agreement':
                        resource.resource_use_agreement = template_df.iat[j, 1]

                    # FixMe:  publications is missing in schema!
                    elif template_df.iat[j, 0] == 'publications':
                        resource.publications = template_df.iat[j, 1]

                    # FixMe:  is_static is missing in schema!
                    elif template_df.iat[j, 0] == 'is_static':
                        resource.is_static = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'Data_Resource':
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
        self.errors = []
        self.success = True
        self.model_data = {}
        self.resource_type = None
        self.source = None

