import os
import logging

ENV_CONFIG_LOCATION = 'PCOR_GEN3_CONFIG_LOCATION'

logger = logging.getLogger(__name__)


class PcorIntermediateProgramModel:
    """
    Represents a program
    """
    def __init__(self):
        self.id = None
        self.program_name = None
        self.short_name = None
        self.program_type = None
        self.program_url = None
        self.dbgap_accession_number = None


class PcorIntermediateProjectModel:

    def __init__(self):
        self.program = None
        # project
        self.availability_mechanism = None
        self.availability_type = None
        self.code = None
        self.complete = None
        self.date_collected = None
        self.dbgap_accession_number = None
        self.id = None
        self.investigator_affiliation = None
        self.investigator_name = None
        self.name = None
        self.short_name = None
        self.support_source = None
        self.support_id = None
        self.program_id = None
        self.submitter_id = None # TODO: make sure sub id carried forward to update
        self.project_type = None
        self.project_url = None
        self.description = None


class PcorIntermediateResourceModel:
    """
    Represents an intermediate data model from some source (e.g. spreadsheet or CEDAR) that is to be ingested into Gen3
    This allows introduction of new curation tools that will follow the same pipeline on the Gen3 side
    """

    def __init__(self):

        self.project = None
        # resource
        self.submitter_id = None
        self.created_datetime = None
        self.id = None
        self.name = None
        self.short_name = None
        self.resource_id = None
        self.resource_type = None
        self.description = None
        self.citation = None
        self.payment_required = None
        self.domain = []
        self.keywords = []
        self.license_type = None
        self.license_text = None
        self.verification_datetime = None
        self.resource_use_agreement = 'false'
        self.resource_contact = None
        self.resource_link = None


class SubmitResponse:
    """
    Represents the data about an object after submission, showing
    the result
    """

    def __init__(self):
        self.project_id = None
        self.type = None
        self.id = None
        self.submitter_id = None


class PcorProgramModel:
    """
    A program in Gen3
    """

    def __init__(self):
        self.name = None
        self.dbgap_accession_number = None


class PcorGeospatialDataResourceModel:
    """
    Represents a geospatial data resource subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = None
        self.comments = None
        self.intended_use = None
        self.source_name = None
        self.source_url = None
        self.update_frequency = None
        self.includes_citizen_collected = None
        self.has_api = "false"
        self.has_visualization_tool = "false"
        self.measures = []
        self.measurement_method = None
        self.time_extent_start = None
        self.time_extent_end = None
        self.times_available_comment = None
        self.temporal_resolution = None
        self.spatial_coverage = None
        self.spatial_resolution = None
        self.spatial_bounding_box = None
        self.geo_ref_system = None
        self.geometry_type = None
        self.geometry_source = None
        self.geographic_feature = None
        self.model_methods = None
        self.exposure_media = []
        self.project_id = None
        self.project_submitter_id = None
        self.resource_id = None
        self.resource_submitter_id = None


class PcorDiscoveryMetadata:
    """
    Represents data for Discovery presentation of a resource
    """

    def __init__(self):
        self.tags = []
        self.adv_search_filters = []
        self.program_name = None
        self.program_type = None
        self.program_url = None
        self.project_type = None
        self.project_url = None
        self.project_description = None
        self.name = None
        self.short_name = None
        self.payment_required = None
        self.verification_datetime = None
        self.investigator_name = None
        self.investigator_affiliation = None
        self.comment = None # collapses intended_use and other descriptions
        self.short_name = None
        self.description = None
        self.support_source = None
        self.source_url = None
        self.citation = None
        self.domain = None
        self.has_api = None
        self.has_visualization_tool = None
        self.is_citizen_collected = None
        self.license_type = None
        self.license_text = None
        self.resource_use_agreement = None
        self.resource_contact = None
        self.resource_id = None
        self.resource_url = None
        self.measures = [] # convert to tags/filters
        self.exposure_media = [] # convert to tags/filters
        self.tool_type = None # tags/filters?
        self.type = None


class Tag:
    """
    Tag struct in discovery metadata
    """

    def __init__(self):
        self.name = None
        self.category = None


class AdvSearchFilter:
    """
    advSearchFilters struct for discovery metadata
    """

    def __init__(self):
        self.key = None
        self.value = None


class PcorPopDataResourceModel:
    """
    Represents a pop data resource subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = None
        self.project_id = None
        self.project_submitter_id = None
        self.resource_id = None
        self.resource_submitter_id = None
        self.created_datetime = None
        self.state = None
        self.updated_datetime = None
        self.comments = None
        self.intended_use = None
        self.source_name = None
        self.source_url = None
        self.update_frequency = None
        self.includes_citizen_collected = None
        self.has_api = "false"
        self.has_visualization_tool = "false"
        self.time_extent_start = None
        self.time_extent_end = None
        self.times_available_comment = None
        self.spatial_resolution = None
        self.spatial_coverage = None
        self.spatial_bounding_box = None
        self.geometry_type = None
        self.geometry_source = None
        self.population = []
        self.vulnerable_population = []
        self.exposures = []
        self.outcomes = []
        self.model_methods = None


class PcorGeoToolModel:
    """
    Represents a geospatial tool resource subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = None
        self.project_id = None
        self.project_submitter_id = None
        self.resource_id = None
        self.resource_submitter_id = None
        self.created_datetime = None
        self.state = None
        self.submitter_id = None
        self.updated_datetime = None
        self.tool_type = None
        self.usage_type = None
        self.operating_system = []
        self.languages = []
        self.input_formats = []
        self.output_formats = []
        self.time_extent_start = None
        self.time_extent_end = None
        self.times_available_comment = None
        self.temporal_resolution = None
        self.spatial_resolution = None
        self.spatial_coverage = None
        self.spatial_bounding_box = None
        self.geometry_type = None
        self.geometry_source = None
        self.model_methods = None
        self.resource_link = None








