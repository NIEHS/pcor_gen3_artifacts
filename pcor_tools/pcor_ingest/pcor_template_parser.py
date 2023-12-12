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


class PcorTemplateParser:
    """
    A parent class for a parser of a PCOR spreadsheet template for a type
    """

    def __init__(self):
        # Regular expression pattern to match "yyyy"
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
        df = pd.read_excel(template_absolute_path, sheet_name=0, engine='openpyxl')

        try:
            result.model_data["submission"] = self.extract_submission_data(df)
        except Exception as err:
            logger.error("exception parsing submission: %s" % str(err))
            result.success = False
            result.errors.append("error parsing submission: %s" % str(err))
            result.traceback = traceback.format_exc()
            result.message = str(err)
            return

        try:

            program = self.extract_program_data(df)
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
            project = self.extract_project_data(df)
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
            resource = self.extract_resource_data(df)
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

    @staticmethod
    def extract_submission_data(template_df):
        """
        Given a pandas dataframe with the template date, extract out the submission related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProgramModel with program data from ss
        """

        # loop thru the template until the marker 'SUBMITTER' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the SUBMITTER stanza")
        submission = PcorSubmissionInfoModel()
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Submitter':
                logging.debug("found Submitter")
                for j in range(i, ss_rows):
                    if template_df.iat[j, 0] == 'submitter_name':
                        submission.curator_name = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'submitter_email':
                        submission.curator_email = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'comment':
                        submission.curation_comment = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'Program':
                        # validate needed props
                        return submission

        logger.warning("no submission found, return null")
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
                    if template_df.iat[j, 0] == 'project_GUID':
                        project.submitter_id = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_name':
                        project.long_name = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_short_name':
                        project.short_name = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        #if project_short_name is not empty, use it for project.code
                        if project.short_name:
                            project.name = project.short_name.replace(' ', '').strip()
                            project.code = project.name
                    elif template_df.iat[j, 0] == 'project_sponsor':
                        project.project_sponsor = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_sponsor_other':
                        project.project_sponsor_other = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_sponsor_type':
                        project.project_sponsor_type = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_sponsor_type_other':
                        project.project_sponsor_type_other = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_url':
                        project.project_url = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'project_description':
                        project.description = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    # FixMe:  following things are missing in template!
                    elif template_df.iat[j, 0] == 'date collected':
                        project.date_collected = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'complete':
                        project.complete = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'availability type':
                        project.availability_type = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'Resource':
                        # validate needed props and guid assignment
                        if project.submitter_id == "" or project.submitter_id is None:
                            project.submitter_id = str(uuid.uuid4())
                        if project.code == "" or project.code is None:
                            project.code = str(uuid.uuid4())
                        if project.dbgap_accession_number == "" or project.dbgap_accession_number is None:
                            project.dbgap_accession_number = project.submitter_id
                        return project

        logger.warning("no program found, return null")
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
                    if template_df.iat[j, 0] == 'resource_GUID':
                        resource.submitter_id = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'resource_name':
                        resource.long_name = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'resource_short_name':
                        resource.short_name = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        # cleanup short name and use it as unique resource short name, no special characters or spaces
                        # do not use sanitize_column()
                        resource.name = str(template_df.iat[j, 1]).replace(' ', '').replace('-', '').strip()
                    elif template_df.iat[j, 0] == 'resource_type':
                        resource.resource_type = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'resource_url':
                        resource.resource_url = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'resource_description':
                        resource.description = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'domain':
                        resource.domain = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'domain_other':
                        resource.domain_other = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'keywords':
                        resource.keywords = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'access_type':
                        resource.access_type = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'payment_required':
                        resource.payment_required = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'date_added':
                        resource.created_datetime = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'date_updated':
                        resource.updated_datetime = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'date_verified':
                        resource.verification_datetime = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'resource_reference':
                        resource.resource_reference = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'resource_use_agreement':
                        resource.resource_use_agreement = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'publications':
                       resource.publications = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'is_static':
                        resource.is_static = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if str(resource.is_static).lower() == 'no':
                            resource.is_static = False
                        elif str(resource.is_static).lower() == 'yes':
                            resource.is_static = True
                    elif template_df.iat[j, 0] == 'Data_Resource' or template_df.iat[j, 0] == 'Tool_Resource':

                        # validate needed props and guid assignment
                        if resource.submitter_id is None or resource.submitter_id == '':
                            resource.submitter_id = str(uuid.uuid4())

                        return resource

        logger.warning("no program found, return null")
        return None

    @staticmethod
    def make_complex_array(value):
        clean_value = PcorTemplateParser.sanitize_column(value)
        temp_list = []
        if clean_value:
            clean_value = re.sub(r'\\n', '\n', value) #unescape newline for split
            temp_list = str(clean_value).splitlines()
            if temp_list and len(temp_list) == 1:
                return PcorTemplateParser.make_array(temp_list[0])

        return temp_list

    @staticmethod
    def make_array(value):
        """
        Just avoiding 'None' when parsing spreadsheet
        Parameters
        ----------
        value string to split into array

        Returns
        -------

        """
        result = []
        if value:
            result = value.split(",")
            result = list(filter(bool, result)) #clean up any null items
        return result

    @staticmethod
    def sanitize_column(value):
        if isinstance(value, str):
            if not value:
                return None
            # escape double quotes inside string
            value = re.sub(r'\d\.\s+', '', value)
            value = re.sub(r'[•●]\s+', '',value)
            value = re.sub('\n',  '\\\\n', value) #must escape newlines for strings they are not valid json
            return value.strip().replace('"', '\\"')
        if isinstance(value, float):
            if math.isnan(value):
                return None
            else:
                return str(value)
        return value

    @staticmethod
    def formate_date_time(string):
        # use dummy
        date_string = '2023/01/01T12:00:00Z'
        datetime_obj = datetime.strptime(date_string, "%Y/%m/%dT%H:%M:%SZ")
        formatted_datetime = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        '''
        # Regular expression pattern to match "yyyy"
        pattern = r"\b(\d{4})\b"

        # Find the year in the string
        match = re.search(pattern, string)

        if match:
            year = int(match.group(1))
            # Replace the matched year with a formatted datetime string
            datetime_str = datetime(year, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
            modified_string = string[:match.start()] + datetime_str + string[match.end():]
            return modified_string
        '''
        return formatted_datetime
