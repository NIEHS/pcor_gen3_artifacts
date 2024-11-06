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
    PcorSubmissionInfoModel, PcorGeospatialDataResourceModel, \
    PcorPopDataResourceModel

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

        if "GEOEXPOSURE DATA" in contents_json:
            geoexposure_data = CedarResourceParser.extract_geoexposure_data(contents_json)
            result.model_data["geospatial_data_resource"] = geoexposure_data
        if "POPULATION DATA RESORCE" in contents_json:
            population_data = CedarResourceParser.extract_population_data(contents_json)
            result.model_data["population_data_resource"] = population_data

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
        if contents_json["SUBMITTER"]["comment"]["@value"]:
            submission.curation_comment = contents_json["SUBMITTER"]["comment"]["@value"]

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
        project.id = contents_json["PROJECT"]["ProjecCode"]["@value"]
        project.name = contents_json["PROJECT"]["project_name"]["@value"]
        project.short_name = contents_json["PROJECT"]["project_short_name"]["@value"]
        project.code = contents_json["PROJECT"]["ProjecCode"]["@value"]

        sponsors_in_json = contents_json["PROJECT"]["project_sponsor"]
        for sponsor in sponsors_in_json:
            if sponsor["@value"]:
               project.project_sponsor.append(sponsor["@value"])

        sponsors_in_json = contents_json["PROJECT"]["project_sponsor_other"]
        for sponsor in sponsors_in_json:
            if sponsor["@value"]:
                project.project_sponsor_other.append(sponsor["@value"])


        sponsor_types = contents_json["PROJECT"]["project_sponsor_type"]
        for item in sponsor_types:
            if item["@value"]:
                project.project_sponsor_type.append(item["@value"])

        sponsor_other = contents_json["PROJECT"]["project_sponsor_type_other"]
        for type in sponsor_other:
            if type["@value"]:
                project.project_sponsor_type_other.append(type["@value"])

        project.project_url = contents_json["PROJECT"]["project_url"]["@id"]
        project.dbgap_accession_number = project.code

        project.project_url = contents_json["PROJECT"]["project_url"]["@id"]

        PcorTemplateParser.process_project_identifiers(project)

        return project


    @staticmethod
    def extract_resource_data(contents_json):
        """
        Given CEDAR JSON-LD with the template date, extract out the resource related data
        :param contents_json: cedar json
        :return: PcorResourceModel with resource data
        """

        resource = PcorIntermediateResourceModel()
        resource.id =  contents_json["RESOURCE"]["resource_GUID"]["@value"]
        resource.resource_type =  contents_json["RESOURCE"]["resource_type"]["@value"]
        resource.name = contents_json["RESOURCE"]["resource_name"]["@value"]
        resource.short_name = contents_json["RESOURCE"]["resource_short_name"]["@value"]

        resource.resource_url =  contents_json["RESOURCE"]["resource_url"]["@id"]
        resource.description = contents_json["RESOURCE"]["resource_description"]["@value"]

        for domain in contents_json["RESOURCE"]["domain"]:
            if domain["@value"]:
                resource.domain.append(domain["@value"])

        for domain in contents_json["RESOURCE"]["domain_other"]:
            if domain["@value"]:
                resource.domain_other.append(domain["@value"])

        resource.access_type = contents_json["RESOURCE"]["access_type"]["@value"]
        resource.created_datetime = contents_json["pav:createdOn"]
        resource.updated_datetime = contents_json["pav:lastUpdatedOn"]

        resource.verification_datetime = contents_json["RESOURCE"]["date_verified"]["@value"]

        for publication_citation in contents_json["RESOURCE"]["Publication"]["publication_citation"]:
            resource.publications.append(publication_citation["@value"])

        for publication_link in contents_json["RESOURCE"]["Publication"]["publication_link"]:
            resource.publication_links.append(publication_link["@id"])

        for keyword in contents_json["RESOURCE"]["keywords"]:
            if keyword["@value"]:
                resource.keywords.append(keyword["@value"])

        resource.payment_required = PcorTemplateParser.sanitize_boolean(
                    contents_json["RESOURCE"]["payment_required"]["@value"])

        resource.resource_reference = contents_json["RESOURCE"]["Resource Reference_150"]["resource_reference"]["@value"]
        resource.resource_reference_link = contents_json["RESOURCE"]["Resource Reference_150"]["resource_reference_link"]["@id"]

        resource.resource_use_agreement = contents_json["RESOURCE"]["Resource Use Agreement_150"]["resource_use_agreement"]["@value"]
        resource.resource_use_agreement_link = contents_json["RESOURCE"]["Resource Use Agreement_150"]["resource_use_agreement_link"]["@id"]

        resource.is_static = PcorTemplateParser.sanitize_boolean(contents_json["RESOURCE"]["is_static"]["@value"])

        if resource.id is None:
            resource.id = str(uuid.uuid4())

        resource.submitter_id = resource.id

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
        geoexposure.comments = contents_json["DATA RESOURCE"]["Comments"]["@value"]
        geoexposure.intended_use = contents_json["DATA RESOURCE"]["intended_use"]["@value"]
        geoexposure.sources = contents_json["DATA RESOURCE"]["source_name"]["@value"]

        for source in contents_json["DATA RESOURCE"]["source_name"]:
            if source["@value"]:
                geoexposure.source_name.append(source["@value"])

        geoexposure.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["includes_citizen_collected"]["@value"])

        for update_frequency in contents_json["DATA RESOURCE"]["update_frequency"]:
            if update_frequency["@value"]:
                geoexposure.update_frequency.append(update_frequency["@value"])

        geoexposure.update_frequency_other = contents_json["DATA RESOURCE"]["update_frequency_other"]["@value"]

        geoexposure.has_api = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["has_api"]["@value"])

        geoexposure.has_visualization_tool = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["has_visualization_tool"]["@value"])

        for measure in contents_json["GEOEXPOSURE DATA"]["measures"]:
            if measure["@value"]:
                geoexposure.measures.append(measure["@value"])

        for measure in contents_json["GEOEXPOSURE DATA"]["measures_other"]:
            if measure["@value"]:
                geoexposure.measures_other.append(measure["@value"])

        for measurement_method in contents_json["GEOEXPOSURE DATA"]["measurement_method"]:
            if measurement_method["@value"]:
                geoexposure.measurement_method.append(measurement_method["@value"])

        for measurement_method in contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]:
            if measurement_method["@value"]:
                geoexposure.measurement_method_other.append(measurement_method["@value"])

        geoexposure.time_extent_start_yyyy = (
            PcorTemplateParser.sanitize_column(contents_json["GEOEXPOSURE DATA"]["time_extent_start"]["@value"]))
        geoexposure.time_extent_end_yyyy = (
            PcorTemplateParser.sanitize_column(contents_json["GEOEXPOSURE DATA"]["time_extent_end"]["@value"]))

        geoexposure.time_available_comment = contents_json["GEOEXPOSURE DATA"]["time_available_comment"]["@value"]

        for temporal_resolution in contents_json["GEOEXPOSURE DATA"]["temporal_resolution"]:
            if temporal_resolution["@value"]:
                geoexposure.temporal_resolution.append(temporal_resolution["@value"])

        for temporal_resolution in contents_json["GEOEXPOSURE DATA"]["temporal_resolution_other"]:
            if temporal_resolution["@value"]:
                geoexposure.temporal_resolution_other.append(temporal_resolution["@value"])

        for spatial_resolution in contents_json["GEOEXPOSURE DATA"]["spatial_resolution"]:
            if spatial_resolution["@value"]:
                geoexposure.spatial_resolution.append(spatial_resolution["@value"])

        for spatial_resolution in contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]:
            if spatial_resolution["@value"]:
                geoexposure.spatial_resolution_other.append(spatial_resolution["@value"])

        for spatial_coverage in contents_json["GEOEXPOSURE DATA"]["spatial_coverage"]:
            if spatial_coverage["@value"]:
                geoexposure.spatial_coverage.append(spatial_coverage["@value"])

        for spatial_coverage in contents_json["GEOEXPOSURE DATA"]["spatial_coverage_other"]:
            if spatial_coverage["@value"]:
                geoexposure.spatial_coverage_other.append(spatial_coverage["@value"])

        if contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"]:
            geoexposure.spatial_coverage.append(contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"])

        for box in contents_json["GEOEXPOSURE DATA"]["spatial_bounding_box"]:
            if box["@value"]:
                geoexposure.spatial_bounding_box.append(box["@value"])

        for source in contents_json["GEOEXPOSURE DATA"]["geometry_source"]:
            if source["@value"]:
                geoexposure.geometry_source.append(source["@value"])

        for source in contents_json["GEOEXPOSURE DATA"]["geometry_source_other"]:
            if source["@value"]:
                geoexposure.geometry_source_other.append(source["@value"])

        for model_method in contents_json["GEOEXPOSURE DATA"]["model_methods"]:
            if model_method["@value"]:
                geoexposure.model_methods.append(model_method["@value"])

        for geometry_type in contents_json["GEOEXPOSURE DATA"]["geometry_type"]:
            if geometry_type["@value"]:
                geoexposure.geometry_type.append(geometry_type["@value"])

        for exposure_media in contents_json["GEOEXPOSURE DATA"]["exposure_media"]:
            if exposure_media["@value"]:
                geoexposure.exposure_media.append(exposure_media["@value"])

        for geographic_feature in contents_json["GEOEXPOSURE DATA"]["geographic_feature"]:
            if geographic_feature["@value"]:
                geoexposure.geographic_feature.append(geographic_feature["@value"])

        for feature in contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]:
            if feature["@value"]:
                geoexposure.geographic_feature_other.append(feature["@value"])

        for data_format in contents_json["GEOEXPOSURE DATA"]["data_formats"]:
            if data_format["@value"]:
                geoexposure.data_formats.append(data_format["@value"])

        for data_location in contents_json["GEOEXPOSURE DATA"]["Data Download"]["data_location"]:
            if data_location["@value"]:
                geoexposure.data_location.append(data_location["@value"])

        for data_location in contents_json["GEOEXPOSURE DATA"]["Data Download"]["data_link"]:
            if data_location["@id"]:
                geoexposure.data_link.append(data_location["@id"])

        return geoexposure

    @staticmethod
    def extract_population_data(contents_json):
        """
        extract the population related information from the cedar resource
        :param contents_json: json-ld from cedar
        :return: PcorPopDataResourceModel
        """

        # some of the data is under the required DATA RESOURCE stanza
        if not contents_json["DATA RESOURCE"]:
            raise Exception("missing DATA RESOURCE information in CEDAR json")

        population = PcorPopDataResourceModel()
        # data resource
        data_resource = contents_json["DATA RESOURCE"]
        population.comments = data_resource["comments"]["@value"]
        population.intended_use = data_resource["intended_use"]["@value"]
        for item in data_resource["source_name"]:
            if item["@value"]:
                population.source_name.append(item["@value"])
        for item in data_resource["update_frequency"]:
            if item["@value"]:
                population.update_frequency.append(item["@value"])
        population.update_frequency_other = data_resource["update_frequency_other"]["@value"]
        population.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
            data_resource["includes_citizen_collected"]["@value"])
        population.has_api = PcorTemplateParser.sanitize_boolean(data_resource["has_api"]["@value"])
        population.has_visualization_tool = PcorTemplateParser.sanitize_boolean(
            data_resource["has_visualization_tool"]["@value"])


        # pop data resource
        pop_data_json = contents_json["POPULATION DATA RESORCE"]
        for item in pop_data_json["exposure_media"]:
            if item["@value"]:
                population.exposure_media.append(item["@value"])
        for item in pop_data_json["measures"]:
            if item["@value"]:
                population.measures.append(item["@value"])
        for item in pop_data_json["measures_others"]:
            if item["@value"]:
                population.measures_other.append(item["@value"])
        population.time_extent_start_yyyy = (
            PcorTemplateParser.sanitize_column(pop_data_json["time_extent_start"]["@value"]))
        population.time_extent_end_yyyy = (
            PcorTemplateParser.sanitize_column(pop_data_json["time_extent_end"]["@value"]))
        population.time_available_comment = pop_data_json["time_available_comment"]["@value"]

        for item in pop_data_json["temporal_resolution"]:
            if item["@value"]:
                population.temporal_resolution.append(item["@value"])
        for item in pop_data_json["temporal_resolution_other"]:
            if item["@value"]:
                population.temporal_resolution_other.append(item["@value"])
        for item in pop_data_json["spatial_resolution"]:
            if item["@value"]:
                population.spatial_resolution.append(item["@value"])
        for item in pop_data_json["spatial_resolution_other"]:
            if item["@value"]:
                population.spatial_resolution_other.append(item["@value"])
        for item in pop_data_json["spatial_coverage"]:
            if item["@value"]:
                population.spatial_coverage.append(item["@value"])
        for spatial_coverage in pop_data_json["spatial_coverage_other"]:
            if spatial_coverage["@value"]:
                population.spatial_coverage_other.append(spatial_coverage["@value"])
        for item in pop_data_json["spatial_coverage_specific regions"]:
            if item["@value"]:
                population.spatial_coverage.append(item["@value"])
        for item in pop_data_json["geometry_type"]:
            if item["@value"]:
                population.geometry_type.append(item["@value"])
        for item in pop_data_json["geometry_source"]:
            if item["@value"]:
                population.geometry_source.append(item["@value"])
        for item in pop_data_json["model_methods"]:
            if item["@value"]:
                population.model_methods.append(item["@value"])
        for item in pop_data_json["model_methods"]:
            if item["@value"]:
                population.model_methods_other.append(item["@value"])
        for population_study in pop_data_json["population_studied"]:
            if population_study["@value"]:
                population.population_studied.append(population_study["@value"])
        for item in pop_data_json["population_studied_other"]:
            if item["@value"]:
                population.population_studied_other.append(item["@value"])
        for item in pop_data_json["biospecimens_type"]:
            if item["@value"]:
                population.biospecimens_type.append(item["@value"])
        for item in pop_data_json["data_formats"]:
            if item["@value"]:
                population.data_formats.append(item["@value"])
        population.biospecimens = PcorTemplateParser.sanitize_boolean(
            pop_data_json["biospecimens"]["@value"])
        population.biospecimens = PcorTemplateParser.sanitize_boolean(
            pop_data_json["linkable_encounters"]["@value"])
        population.biospecimens = PcorTemplateParser.sanitize_boolean(
            pop_data_json["individual_level"]["@value"])
        for item in pop_data_json["Data Download"]["data_location"]:
            if item["@value"]:
                population.data_location.append(item["@value"])
        for item in pop_data_json["Data Download"]["data_link"]:
            if item["@id"]:
                population.data_link.append(item["@id"])

        return population






