import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from pcor_ingest.ingest_context import PcorIngestConfiguration

from pcor_cedar.cedar_config import CedarConfig
from pcor_ingest.pcor_template_parser import PcorTemplateParser

from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorIntermediateProgramModel, \
    PcorSubmissionInfoModel, PcorGeospatialDataResourceModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarResourceParser:
    """
    A parent class for a parser of a PCOR Cedar for a type
    """

    def __init__(self):
        self.cedar_config = CedarConfig()
        self.pcor_measures_rollup = PcorMeasuresRollup(self.cedar_config.cedar_properties["measures.location"])
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

        # based on type extract the detailed resource information

        if contents_json["GEOEXPOSURE DATA"]:
            geoexposure_data = CedarResourceParser.extract_geoexposure_data(contents_json)
            result.model_data["geospatial_data_resource"] = geoexposure_data

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
        if contents_json["SUBMITTER"]["Comment"]["@value"]:
            submission.curation_comment = contents_json["SUBMITTER"]["Comment"]["@value"]

        submission.curation_comment = submission.curation_comment + "From CEDAR resource at: " + contents_json["@id"]
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
        project.code = contents_json["PROJECT"]["ProjecCode"]["@value"]
        # if project_short_name is not empty, use it for project.code
        #if project.short_name:
        #    project.name = project.short_name.replace(' ', '').strip()
        #    project.code = project.name

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
        PcorTemplateParser.process_project_identifiers(project)

        return project


    @staticmethod
    def extract_resource_data(contents_json):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param contents_json: cedar json
        :return: PcorResourceModel with resource data
        """

        resource = PcorIntermediateResourceModel()

        resource.name = contents_json["RESOURCE"]["resource_name"]["@value"]
        resource.short_name = contents_json["RESOURCE"]["resource_short_name"]["@value"]
        resource.resource_type =  contents_json["RESOURCE"]["resource_type"]["@value"]
        resource.resource_url =  contents_json["RESOURCE"]["resource_url"]["@value"]
        resource.description = contents_json["RESOURCE"]["resource_description"]["@value"]

        for domain in contents_json["RESOURCE"]["domain"]:
            if domain["@value"]:
                resource.domain.append(domain["@value"])

        for domain in contents_json["RESOURCE"]["domain_other"]:
            if domain["@value"]:
                resource.domain.append(domain["@value"])

        resource.access_type = contents_json["RESOURCE"]["access_type"]["@value"]

        resource.payment_required = PcorTemplateParser.sanitize_boolean(
                    contents_json["RESOURCE"]["payment_required"]["@value"])

        resource.created_datetime = contents_json["RESOURCE"]["date_added"]["@value"]
        resource.updated_datetime = contents_json["RESOURCE"]["Date_updated"]["@value"]
        resource.verification_datetime = contents_json["RESOURCE"]["date_verified"]["@value"]
        resource.resource_reference = contents_json["RESOURCE"]["resource_reference"]["@value"]
        resource.resource_use_agreement = contents_json["RESOURCE"]["resource_use_agreement"]["@value"]

        for publication_citation in contents_json["RESOURCE"]["Publication"]["publication_citation"]:
            resource.publications.append(publication_citation["@value"])

        for publication_link in contents_json["RESOURCE"]["Publication"]["publication_link"]:
            resource.publication_links.append(publication_link["@id"])

        for keyword in contents_json["RESOURCE"]["keywords"]:
            if keyword["@value"]:
                resource.keywords.append(keyword["@value"])

        resource.is_static = PcorTemplateParser.sanitize_boolean(contents_json["RESOURCE"]["is_static"]["@value"])

        if resource.submitter_id is None or resource.submitter_id == '':
            resource.submitter_id = str(uuid.uuid4())
        return resource

    @staticmethod
    def extract_geoexposure_data(contents_json):
        """
        extract the geoexposure related information from the cedar resource
        :param contents_json: json-ld from cedar
        :return: PcorGeospatialDataResourceModel
        """

        # some of the data is under the required DATA RESOURCE stanza
        if not contents_json["DATA RESOURCE"]:
            raise Exception("missing DATA RESOURCE information in CEDAR json")

        geoexposure = PcorGeospatialDataResourceModel()
        geoexposure.comments = contents_json["DATA RESOURCE"]["comments"]["@value"]
        geoexposure.intended_use = contents_json["DATA RESOURCE"]["intended_use"]["@value"]
        geoexposure.sources = contents_json["DATA RESOURCE"]["source_name"]["@value"]

        geoexposure.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["includes_citizen_collected"]["@value"])

        for update_frequency in contents_json["DATA RESOURCE"]["update_frequency"]:
            if update_frequency["@value"]:
                geoexposure.update_frequency.append(update_frequency["@value"])

        geoexposure.has_api = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["has_api"]["@value"])

        geoexposure.has_visualization_tool = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["has_visualization_tool"]["@value"])

        for measure in contents_json["GEOEXPOSURE DATA"]["measures"]:
            geoexposure.measures.append(measure["@value"])

        for measure in contents_json["GEOEXPOSURE DATA"]["measures_other"]:
            if measure["@value"]:
                geoexposure.measures.append(measure["@value"])

        for measurement_method in contents_json["GEOEXPOSURE DATA"]["measurement_method"]:
            if measurement_method["@value"]:
                geoexposure.measurement_method.append(measurement_method["@value"])

        if contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]["@value"]:
            geoexposure.measurement_method.append( contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]["@value"])

        geoexposure.time_extent_start_yyyy = (
            PcorTemplateParser.sanitize_column(contents_json["GEOEXPOSURE DATA"]["time_extent_start"]["@value"]))
        geoexposure.time_extent_end_yyyy = (
            PcorTemplateParser.sanitize_column(contents_json["GEOEXPOSURE DATA"]["time_extent_end"]["@value"]))

        geoexposure.time_available_comment = contents_json["GEOEXPOSURE DATA"]["time_available_comment"]["@value"]

        for temporal_resolution in contents_json["GEOEXPOSURE DATA"]["temporal_resolution"]:
            if temporal_resolution["@value"]:
                geoexposure.temporal_resolution.append(temporal_resolution["@value"])

        for spatial_resolution in contents_json["GEOEXPOSURE DATA"]["spatial_resolution"]:
            geoexposure.spatial_resolution.append(spatial_resolution["@value"])

        if contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]["@value"]:
            geoexposure.spatial_resolution.append(contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]["@value"])

        # FIXME: spatial resolution other not an array

        for spatial_coverage in contents_json["GEOEXPOSURE DATA"]["spatial_coverage"]:
            if spatial_coverage["@value"]:
                geoexposure.spatial_coverage.append(spatial_coverage["@value"])

        if contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"]:
            geoexposure.spatial_coverage.append(contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"])

        geoexposure.spatial_bounding_box = contents_json["GEOEXPOSURE DATA"]["spatial_bounding_box"]["@value"]

        for geometry_type in contents_json["GEOEXPOSURE DATA"]["geometry_type"]:
            if geometry_type["@value"]:
                geoexposure.geometry_type.append(geometry_type["@value"])

        if contents_json["GEOEXPOSURE DATA"]["geometry_source"]["@value"]:
            geoexposure.geometry_source = contents_json["GEOEXPOSURE DATA"]["geometry_source"]["@value"]

        for model_method in contents_json["GEOEXPOSURE DATA"]["model_methods"]:
            if model_method["@value"]:
                geoexposure.model_methods.append(model_method["@value"])

        for exposure_media in contents_json["GEOEXPOSURE DATA"]["exposure_media"]:
            if exposure_media["@value"]:
                geoexposure.exposure_media.append(exposure_media["@value"])

        for geographic_feature in contents_json["GEOEXPOSURE DATA"]["geographic_feature"]:
            if geographic_feature["@value"]:
                geoexposure.geographic_feature.append(geographic_feature["@value"])

        if contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]["@value"]:
            geoexposure.geographic_feature.append(
                contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]["@value"])

        for data_format in contents_json["GEOEXPOSURE DATA"]["data_formats"]:
            if data_format["@value"]:
                geoexposure.data_formats.append(data_format["@value"])

        # FIXME: is array in model
        if contents_json["GEOEXPOSURE DATA"]["data_location"]["@value"]:
            geoexposure.data_location.append(contents_json["GEOEXPOSURE DATA"]["data_location"]["@value"])

        return geoexposure