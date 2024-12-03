import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from IPython.terminal.interactiveshell import black_reformat_handler

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_resource_reader import CedarResourceReader
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_template_parser import PcorTemplateParser

from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorIntermediateProgramModel, \
    PcorSubmissionInfoModel, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorKeyDatasetModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarResourceReader_1_5_0(CedarResourceReader):
    """
    A parent class for a parser of a PCOR Cedar for a type
    """

    def __init__(self):
        CedarResourceReader.__init__(self)

    def parse(self, template_absolute_path, result):

        # example path /deep/documents/foo.xls
        logger.info("parse()")

        """
        Parse a resource at a given absolute path
        :param template_absolute_path: absolute path to the template file
        :param result: PcorTemplateParseResult with the outcome
        """
        warnings.simplefilter(action='ignore', category=UserWarning)
        with open(template_absolute_path, 'r') as f:
            contents_json = json.loads(f.read())

        try:
            submission = CedarResourceReader_1_5_0.extract_submission_data(contents_json)
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
            project = CedarResourceReader_1_5_0.extract_project_data(contents_json)
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
            resource = CedarResourceReader_1_5_0.extract_resource_data(contents_json)
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
            logger.info("geoexposure phase")
            geoexposure_data = CedarResourceReader_1_5_0.extract_geoexposure_data(contents_json)
            result.model_data["geospatial_data_resource"] = geoexposure_data
        elif "POPULATION DATA RESORCE" in contents_json:
            logger.info("population data phase")
            population_data = CedarResourceReader_1_5_0.extract_population_data(contents_json)
            result.model_data["population_data_resource"] = population_data
        elif "KEY DATASETS DATA" in contents_json:
            logger.info("key datasets phase")
            key_datasets_data = CedarResourceReader_1_5_0.extract_key_datasets_data(contents_json)
            result.model_data["key_datasets_data"] = key_datasets_data
        elif "TOOL RESOURCE" in contents_json:
            logger.info("tooL resources phase")
            tools_data = CedarResourceReader_1_5_0.extract_geoexposure_tool_data(contents_json)
            result.model_data["geospatial_tool_resource"] = tools_data
        else:
            raise Exception("unknown data type")


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
        project.name = contents_json["PROJECT"]["project_name"]["@value"]
        project.short_name = contents_json["PROJECT"]["project_short_name"]["@value"]
        project.code = contents_json["PROJECT"]["ProjecCode"]["@value"]

        if type(contents_json["PROJECT"]["project_sponsor"]) in (tuple, list):
            json_val = contents_json["PROJECT"]["project_sponsor"]
            for val in json_val:
                if val["@value"]:
                   project.project_sponsor.append(val["@value"])
        else:
            project.project_sponsor.append(contents_json["PROJECT"]["project_sponsor"]["@value"])

        if type(contents_json["PROJECT"]["project_sponsor_other"]) in (tuple, list):
            json_val = contents_json["PROJECT"]["project_sponsor_other"]
            for val in json_val:
                if val["@value"]:
                    project.project_sponsor_other.append(val["@value"])
        else:
            project.project_sponsor_other.append(contents_json["PROJECT"]["project_sponsor_other"]["@value"])

        json_val = contents_json["PROJECT"]["project_sponsor_type"] # may not be an array
        if type(json_val) in (tuple, list):
            for val in json_val:
                if val["@value"]:
                    project.project_sponsor_type.append(val["@value"])
        else:
            project.project_sponsor_type.append(json_val["@value"])

        project.project_url = contents_json["PROJECT"]["project_url"]["@id"]
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
        resource.resource_url =  contents_json["RESOURCE"]["resource_url"]["@id"]
        resource.description = contents_json["RESOURCE"]["resource_description"]["@value"]

        for domain in contents_json["RESOURCE"]["domain"]:
            if domain["@value"]:
                resource.domain.append(domain["@value"])

        for domain in contents_json["RESOURCE"]["domain_other"]:
            if domain["@value"]:
                resource.domain_other.append(domain["@value"])

        if type(contents_json["RESOURCE"]["access_type"]) in (tuple, list):
            for access_type in contents_json["RESOURCE"]["access_type"]:
                resource.access_type.append(access_type["@value"]) # TODO: changed to array
        else:
            resource.access_type.append(contents_json["RESOURCE"]["access_type"]["@value"])

        if type(contents_json["RESOURCE"]["payment_required"]) in (tuple, list):
            resource.payment_required = PcorTemplateParser.sanitize_boolean(
                    contents_json["RESOURCE"]["payment_required"][0]["@value"])
        else:
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

        if type(contents_json["RESOURCE"]["is_static"]) in (tuple, list):
            resource.is_static = PcorTemplateParser.sanitize_boolean(contents_json["RESOURCE"]["is_static"][0]["@value"])
        else:
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

        try:
            geoexposure.comments = contents_json["DATA RESOURCE"]["comments"]["@value"]
        except KeyError:
            geoexposure.comments = contents_json["DATA RESOURCE"]["Comments"]["@value"]

        geoexposure.intended_use = contents_json["DATA RESOURCE"]["intended_use"]["@value"]
        geoexposure.sources = contents_json["DATA RESOURCE"]["source_name"]["@value"]

        if type(contents_json["DATA RESOURCE"]["includes_citizen_collected"]) in (tuple, list):
            geoexposure.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
                    contents_json["DATA RESOURCE"]["includes_citizen_collected"][0]["@value"])
        else:
            geoexposure.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["includes_citizen_collected"]["@value"])

        for update_frequency in contents_json["DATA RESOURCE"]["update_frequency"]:
            if update_frequency["@value"]:
                geoexposure.update_frequency.append(update_frequency["@value"])

        if type(contents_json["DATA RESOURCE"]["has_api"]) in (tuple, list):
            geoexposure.has_api = PcorTemplateParser.sanitize_boolean(
                    contents_json["DATA RESOURCE"]["has_api"][0]["@value"])
        else:
            geoexposure.has_api = PcorTemplateParser.sanitize_boolean(
                contents_json["DATA RESOURCE"]["has_api"]["@value"])

        if type(contents_json["DATA RESOURCE"]["has_visualization_tool"]) in (tuple, list):
            geoexposure.has_visualization_tool = PcorTemplateParser.sanitize_boolean(
                    contents_json["DATA RESOURCE"]["has_visualization_tool"][0]["@value"])
        else:
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

        if type(contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]) in (tuple, list):
            for method in contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]:
                geoexposure.measurement_method.append(method["@value"])
        else:
            geoexposure.measurement_method.append(
                contents_json["GEOEXPOSURE DATA"]["measurement_method_other"]["@value"])


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

        if type(contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]) in (tuple, list):
            for resolution in contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]:
                geoexposure.spatial_resolution.append(resolution["@value"])
        else:
            geoexposure.spatial_resolution.append(contents_json["GEOEXPOSURE DATA"]["spatial_resolution_other"]["@value"])

        # FIXME: spatial resolution other not an array

        for spatial_coverage in contents_json["GEOEXPOSURE DATA"]["spatial_coverage"]:
            if spatial_coverage["@value"]:
                geoexposure.spatial_coverage.append(spatial_coverage["@value"])

        if type(contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]) in (tuple, list):
            for region in contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]:
                geoexposure.spatial_coverage.append(region["@value"])
        else:
            if contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"]:
                geoexposure.spatial_coverage.append(contents_json["GEOEXPOSURE DATA"]["spatial_coverage_specific_regions"]["@value"])

        if type(contents_json["GEOEXPOSURE DATA"]["spatial_bounding_box"]) in (tuple, list):
            for box in contents_json["GEOEXPOSURE DATA"]["spatial_bounding_box"]:
                geoexposure.spatial_bounding_box.append(box["@value"])
        else:
            geoexposure.spatial_bounding_box.append(
                contents_json["GEOEXPOSURE DATA"]["spatial_bounding_box"]["@value"])

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

        if type(contents_json["GEOEXPOSURE DATA"]["geographic_feature"]) in (tuple, list):
            for geographic_feature in contents_json["GEOEXPOSURE DATA"]["geographic_feature"]:
                if geographic_feature["@value"]:
                    geoexposure.geographic_feature.append(geographic_feature["@value"])
        else:
            geoexposure.geographic_feature.append(contents_json["GEOEXPOSURE DATA"]["geographic_feature"]["@value"])

        if type(contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]) in (tuple, list):
            for feature in contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]:
                geoexposure.geographic_feature.append(
                   feature["@value"])
        else:
            geoexposure.geographic_feature.append(contents_json["GEOEXPOSURE DATA"]["geographic_feature_other"]["@value"])

        for data_format in contents_json["GEOEXPOSURE DATA"]["data_formats"]:
            if data_format["@value"]:
                geoexposure.data_formats.append(data_format["@value"])

        if type(contents_json["GEOEXPOSURE DATA"]["data_location"]) in (tuple, list):
            for location in contents_json["GEOEXPOSURE DATA"]["data_location"]:
                val = location["@value"]
                if CedarResourceReader.validate_url(val):
                    geoexposure.data_link.append(val)
                else:
                    geoexposure.data_location.append(val)
        else:
            val = contents_json["GEOEXPOSURE DATA"]["data_location"]["@value"]
            if CedarResourceReader.validate_url(val):
                geoexposure.data_link.append(val)
            else:
                geoexposure.data_location.append(val)

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
        population.comments = data_resource["Comments"]["@value"]
        population.intended_use = data_resource["intended_use"]["@value"]

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
            PcorTemplateParser.format_date_time(pop_data_json["time_extent_start"]["@value"]))
        population.time_extent_end_yyyy = (
            PcorTemplateParser.format_date_time(pop_data_json["time_extent_end"]["@value"]))
        population.time_available_comment = pop_data_json["time_available_comment"]["@value"]

        if type(pop_data_json["temporal_resolution"]) in (tuple, list):
            for item in pop_data_json["temporal_resolution"]:
                if item["@value"]:
                    population.temporal_resolution.append(item["@value"])
        else:
            population.temporal_resolution.append(pop_data_json["temporal_resolution"]["@value"])

        for item in pop_data_json["temporal_resolution_other"]:
            if item["@value"]:
                population.temporal_resolution_other.append(item["@value"])

        if type(pop_data_json["spatial_resolution"]) in (tuple, list):
            for item in pop_data_json["spatial_resolution"]:
                if item["@value"]:
                    population.spatial_resolution.append(item["@value"])
                else:
                    population.spatial_resolution.append(pop_data_json["spatial_resolution"]["@value"])

        for item in pop_data_json["spatial_resolution_other"]:
            if item["@value"]:
                population.spatial_resolution_other.append(item["@value"])

        for item in pop_data_json["spatial_coverage"]:
            if item["@value"]:
                population.spatial_coverage.append(item["@value"])

        for spatial_coverage in pop_data_json["spatial_coverage_other"]:
            if spatial_coverage["@value"]:
                population.spatial_coverage_other.append(spatial_coverage["@value"])

        for item in pop_data_json["geometry_type"]:
            if item["@value"]:
                population.geometry_type.append(item["@value"])

        for item in pop_data_json["geometry_source"]:
            if item["@value"]:
                population.geometry_source.append(item["@value"])
        for item in pop_data_json["geometry_source_other"]:
            if item["@value"]:
                population.geometry_source_other.append(item["@value"])

        for item in pop_data_json["model_methods"]:
            if item["@value"]:
                population.model_methods.append(item["@value"])

        for item in pop_data_json["model_methods_other"]:
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

        population.linkable_encounters = PcorTemplateParser.sanitize_boolean(
            pop_data_json["linkable_encounters"]["@value"])

        population.individual_level = PcorTemplateParser.sanitize_boolean(
            pop_data_json["individual_level"]["@value"])

        for item in pop_data_json["Data Download"]["data_location"]:
            if item["@value"]:
                population.data_location.append(item["@value"])

        for item in pop_data_json["Data Download"]["data_link"]:
            if item["@id"]:
                population.data_link.append(item["@id"])
        return population

    @staticmethod
    def extract_key_datasets_data(contents_json):
        """
        extract the key dataset related information from the cedar resource
        :param contents_json: json-ld from cedar
        :return: PcorPopDataResourceModel
        """

        # some of the data is under the required DATA RESOURCE stanza
        if not contents_json["DATA RESOURCE"]:
            raise Exception("missing DATA RESOURCE information in CEDAR json")

        key_dataset = PcorKeyDatasetModel()

        # data resource
        data_resource = contents_json["DATA RESOURCE"]
        for item in data_resource["source_name"]:
            if item["@value"]:
                key_dataset.source_name.append(item["@value"])
        for item in data_resource["update_frequency"]:
            if item["@value"]:
                key_dataset.update_frequency.append(item["@value"])
        key_dataset.update_frequency_other = data_resource["update_frequency_other"]["@value"]
        key_dataset.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(
            data_resource["includes_citizen_collected"]["@value"])
        key_dataset.has_api = PcorTemplateParser.sanitize_boolean(data_resource["has_api"]["@value"])
        key_dataset.has_visualization_tool = PcorTemplateParser.sanitize_boolean(
            data_resource["has_visualization_tool"]["@value"])
        key_dataset.comments = data_resource["Comments"]["@value"]
        key_dataset.intended_use = data_resource["intended_use"]["@value"]

        # Key datasets data
        key_data_json = contents_json["KEY DATASETS DATA"]
        for item in key_data_json["measurement_method"]:
            if item["@value"]:
                key_dataset.measurement_method.append(item["@value"])
        for item in key_data_json["measurement_method_other"]:
            if item["@value"]:
                key_dataset.measurement_method_other.append(item["@value"])
        key_dataset.time_extent_start_yyyy = (
            PcorTemplateParser.format_date_time(key_data_json["time_extent_start"]["@value"]))
        key_dataset.time_extent_end_yyyy = (
            PcorTemplateParser.format_date_time(key_data_json["time_extent_end"]["@value"]))
        key_dataset.time_available_comment = key_data_json["time_available_comment"]["@value"]
        for item in key_data_json["temporal_resolution"]:
            if item["@value"]:
                key_dataset.temporal_resolution.append(item["@value"])
        for item in key_data_json["temporal_resolution_other"]:
            if item["@value"]:
                key_dataset.temporal_resolution_other.append(item["@value"])
        for item in key_data_json["spatial_resolution"]:
            if item["@value"]:
                key_dataset.spatial_resolution.append(item["@value"])
        for item in key_data_json["spatial_resolution_other"]:
            if item["@value"]:
                key_dataset.spatial_resolution_other.append(item["@value"])
        for item in key_data_json["spatial_coverage"]:
            if item["@value"]:
                key_dataset.spatial_coverage.append(item["@value"])
        for item in key_data_json["spatial_coverage_other"]:
            if item["@value"]:
                key_dataset.spatial_coverage_other.append(item["@value"])
        for item in key_data_json["spatial_bounding_box"]:
            if item["@value"]:
                key_dataset.spatial_bounding_box.append(item["@value"])
        for item in key_data_json["geometry_type"]:
            if item["@value"]:
                key_dataset.geometry_type.append(item["@value"])
        for item in key_data_json["geometry_source"]:
            if item["@value"]:
                key_dataset.geometry_source.append(item["@value"])
        for item in key_data_json["geometry_source_other"]:
            if item["@value"]:
                key_dataset.geometry_source_other.append(item["@value"])
        for item in key_data_json["model_methods"]:
            if item["@value"]:
                key_dataset.model_methods.append(item["@value"])
        for item in key_data_json["model_methods_other"]:
            if item["@value"]:
                key_dataset.model_methods_other.append(item["@value"])
        for item in key_data_json["exposure_media"]:
            if item["@value"]:
                key_dataset.exposure_media.append(item["@value"])
        for item in key_data_json["geographic_feature"]:
            if item["@value"]:
                key_dataset.geographic_feature.append(item["@value"])
        for item in key_data_json["geographic_feature_other"]:
            if item["@value"]:
                key_dataset.geographic_feature_other.append(item["@value"])
        for item in key_data_json["data_formats"]:
            if item["@value"]:
                key_dataset.data_formats.append(item["@value"])
        for item in key_data_json["Data Download"]["data_location"]:
            if item["@value"]:
                key_dataset.data_location.append(item["@value"])
        for item in key_data_json["Data Download"]["data_link"]:
            if item["@id"]:
                key_dataset.data_link.append(item["@id"])
        return key_dataset

    @staticmethod
    def extract_geoexposure_tool_data(contents_json):
        """
        extract the geoexposure tool related information from the cedar resource
        :param contents_json: json-ld from cedar
        :return: PcorGeospatialDataResourceModel
        """

        # some of the data is under the required DATA RESOURCE stanza
        if not contents_json["TOOL RESOURCE"]:
            raise Exception("missing TOOL RESOURCE information in CEDAR json")

        geotool = PcorGeoToolModel()

        body = contents_json["TOOL RESOURCE"]

        geotool.tool_type.append(body["tool_type"]["@value"])
        geotool.operating_system.append(body["operating_system"]["@value"])

        for entry in body["operating_system_other"]:
            if entry["@value"]:
                geotool.operating_system_other.append(entry["@value"])

        for lang in body["languages"]:
            if lang["@value"]:
                geotool.languages.append(lang["@value"])

        for lang in body["languages_other"]:
            if lang["@value"]:
                geotool.languages_other.append(lang["@value"])

        for license_type in body["license_type"]:
            if license_type["@value"]:
                geotool.license_type.append(license_type["@value"])

        for license_type in body["license_type_other"]:
            if license_type["@value"]:
                geotool.license_type_other.append(license_type["@value"])

        for aud in body["suggested_audience"]:
            if aud["@value"]:
                geotool.suggested_audience.append(aud["@value"])

        geotool.is_open = PcorTemplateParser.sanitize_boolean(
            body["is_open"]["@value"])

        geotool.intended_use = body["intended_use"]["@value"]

        return geotool
