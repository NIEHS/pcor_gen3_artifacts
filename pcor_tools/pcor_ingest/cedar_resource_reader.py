import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from pcor_ingest.pcor_template_parser import PcorTemplateParser

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
            submission = CedarResourceParser.extract_submission_data(contents_json)
            submission.submit_location = template_absolute_path
            result.model_data["submission"] = submission
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
            project = CedarResourceParser.extract_project_data(contents_json)
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
            resource = CedarResourceParser.extract_resource_data(contents_json)
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
    def extract_program_data(contents_json):
        """
        Given a resource, extract out the program related data
        :param contents_json: json representation of resource
        :return: PcorProgramModel with program data
        """

        program = PcorIntermediateProgramModel()
        program.dbgap_accession_number = contents_json["PROGRAM"]["@id"] # FIXME: add to tpl
        program.name = contents_json["PROGRAM"]["Program_name"]["@value"]
        if program.dbgap_accession_number == "" or program.dbgap_accession_number is None:
            program.dbgap_accession_number = program.name
        return program

    @staticmethod
    def extract_submission_data(contents_json):
        """
        extract the submission related information from the cedar resource
        :param contents_json: json-ld from cedar
        :return: PcorSubmissionInfoModel with submission data
        """

        submission = PcorSubmissionInfoModel()

        submission.curator_name = contents_json["SUBMITTER"]["submitter_name"]["@value"]
        submission.curator_email = contents_json["SUBMITTER"]["submitter_email"]["@value"]
        submission.curation_comment = contents_json["SUBMITTER"]["Comment"]["@value"]
        submission.template_source = contents_json["@id"]

        return submission

    @staticmethod
    def extract_project_data(contents_json):
        """
        extract project related data
        :param contents_json: json-ld from cedar
        :return: PcorProjectModel with project data
        """
        project = PcorIntermediateProjectModel()
        project.long_name = contents_json["PROJECT"]["project_name"]["@value"]
        project.short_name = contents_json["PROJECT"]["project_short_name"]["@value"]
        # if project_short_name is not empty, use it for project.code
        if project.short_name:
            project.name = project.short_name.replace(' ', '').strip()
            project.code = project.name

        sponsors_in_json = contents_json["PROJECT"]["project_sponsor"]
        for sponsor in sponsors_in_json:
            if sponsor["@value"]:
               project.project_sponsor.append(sponsor["@value"])

        sponsor_other =  contents_json["PROJECT"]["project_sponsor_other"]["@value"]
        if sponsor_other:
            project.project_sponsor.append(sponsor_other)

        sponsor_types = contents_json["PROJECT"]["project_sponsor_type"]
        for type in sponsor_types:
            if  type["@value"]:
                project.project_sponsor_type.append(type["@value"])

        sponsor_other = contents_json["PROJECT"]["project_sponsor_type_other"]["@value"]
        if sponsor_other:
            project.project_sponsor_type.append(sponsor_other)


        project.project_url = contents_json["PROJECT"]["project_url"]["@value"]
        #project.description = contents_json["PROJECT"]["project_url"]["@value"] FIXME: missing?

        if project.submitter_id == "" or project.submitter_id is None:
            project.submitter_id = str(uuid.uuid4())
        if project.code == "" or project.code is None:
            project.code = str(uuid.uuid4())
        if project.dbgap_accession_number == "" or project.dbgap_accession_number is None:
            project.dbgap_accession_number = project.submitter_id

        return project

    @staticmethod
    def extract_resource_data(contents_json):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        resource = PcorIntermediateResourceModel()

       #resource.submitter_id = # not supplied
        #resource.long_name = contents_json["RESOURCE"]["resource_name"]
        #resource.short_name = contents_json["RESOURCE"]["resource_name"] # FIXME: unneeded?
        # cleanup short name and use it as unique resource short name, no special characters or spaces
        # do not use sanitize_column()
        resource.name = contents_json["RESOURCE"]["resource_name"]["@value"]
        resource.resource_type =  contents_json["RESOURCE"]["resource_type"]["@value"]
        resource.resource_url =  contents_json["RESOURCE"]["resource_url"]["@value"]
        resource.description = contents_json["RESOURCE"]["resource_description"]["@value"]

        # FIXME: domain is not a multi-entry at this point
        if contents_json["RESOURCE"]["domain"]["@value"]:
            resource.domain.append(contents_json["RESOURCE"]["domain"]["@value"])

        if contents_json["RESOURCE"]["domain_other"]["@value"]:
            resource.domain.append(contents_json["RESOURCE"]["domain_other"]["@value"])

        #FIXME: keywords is not multi-entry at this point
        if contents_json["RESOURCE"]["keywords"]["@value"]:
            resource.keywords.append(contents_json["RESOURCE"]["keywords"]["@value"])

        resource.access_type = contents_json["RESOURCE"]["access_type"]["@value"]
        # FIXME: payment required an array?
        #resource.payment_required = PcorTemplateParser.sanitize_boolean(contents_json["RESOURCE"]["payment_required"]["@value"])
        resource.created_datetime = contents_json["RESOURCE"]["date_added"]["@value"]
        resource.updated_datetime = contents_json["RESOURCE"]["Date_updated"]["@value"]
        resource.verification_datetime = contents_json["RESOURCE"]["date_verified"]["@value"] # FIXME: irregular case
        resource.resource_reference = contents_json["RESOURCE"]["resource_url"]["@value"]
        resource.resource_use_agreement = contents_json["RESOURCE"]["resource_use_agreement"]["@value"]
        #FIXME: publication not an array

        #if contents_json["RESOURCE"]["Publication"]["publication_citation"]["@value"] | contents_json["RESOURCE"]["Publication"]["publication_link"]["@value"]:
        #    resource.publications.append(contents_json["RESOURCE"]["Publication"]["publication_citation"]["@value"])
           # resource.publication_links.append(contents_json["RESOURCE"]["Publication"]["publication_link"]["@value"])
        # FIXME: should not be an array?
        #resource.is_static = PcorTemplateParser.sanitize_boolean(contents_json["RESOURCE"]["is_static"]["@value"])

        if resource.submitter_id is None or resource.submitter_id == '':
            resource.submitter_id = str(uuid.uuid4())
        return resource

