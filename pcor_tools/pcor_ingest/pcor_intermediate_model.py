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
        self.name = None
        self.dbgap_accession_number = None


class PcorIntermediateProjectModel:

    def __init__(self):
        self.program = None
        self.program_id = None

        # project
        self.id = None
        self.name = None
        self.long_name = None
        self.project_sponsor = None
        self.project_sponsor_other = None
        self.project_sponsor_type = None
        self.project_url = None
        self.description = None
        self.code = None
        self.submitter_id = None  # TODO: make sure sub id carried forward to update
        self.availability_mechanism = None
        self.availability_type = None
        self.complete = None
        self.date_collected = None
        self.dbgap_accession_number = None




class PcorIntermediateResourceModel:
    """
    Represents an intermediate data model from some source (e.g. spreadsheet or CEDAR) that is to be ingested into Gen3
    This allows introduction of new curation tools that will follow the same pipeline on the Gen3 side
    """

    def __init__(self):

        self.project = ""
        # resource
        self.submitter_id = ""
        self.created_datetime = ""
        self.updated_datetime = ""
        self.id = ""
        self.name = ""
        self.short_name = ""
        self.resource_id = ""
        self.resource_type = ""
        self.description = ""
        self.citation = ""
        self.payment_required = ""
        self.domain = []
        self.keywords = []
        self.access_type = ""
        self.license_type = ""
        self.license_text = ""
        self.verification_datetime = ""
        self.resource_use_agreement = ""
        self.resource_contact = ""
        self.resource_link = ""
        #self.publications = ""
        self.is_static = ""



class SubmitResponse:
    """
    Represents the data about an object after submission, showing
    the result
    """

    def __init__(self):
        self.project_id = ""
        self.type = ""
        self.id = ""
        self.submitter_id = ""


class PcorProgramModel:
    """
    A program in Gen3
    """

    def __init__(self):
        self.name = ""
        self.dbgap_accession_number = ""


class PcorGeospatialDataResourceModel:
    """
    Represents a geospatial data resource subtype
    """

    def __init__(self):
        self.data_type = ""
        self.pcor_intermediate_resource_model = None
        self.submitter_id = ""
        self.comments = ""
        self.intended_use = ""
        self.source_name = ""
        self.source_url = ""
        self.update_frequency = ""
        self.includes_citizen_collected = "false"
        self.has_api = "false"
        self.has_visualization_tool = "false"
        self.measures = []
        self.measurement_method = ""
        self.time_extent_start = ""
        self.time_extent_end = ""
        self.time_available_comment = ""
        self.temporal_resolution = ""
        self.spatial_coverage = ""
        self.spatial_resolution = ""
        self.spatial_bounding_box = ""
        self.geo_ref_system = ""
        self.geometry_type = ""
        self.geometry_source = ""
        self.geographic_feature = ""
        self.model_methods = ""
        self.exposure_media = []
        self.project_id = ""
        self.project_submitter_id = ""
        self.resource_id = ""
        self.resource_submitter_id = ""


class PcorDiscoveryMetadata:
    """
    Represents data for Discovery presentation of a resource
    """

    def __init__(self):
        self.tags = []
        self.adv_search_filters = []
        self.program_name = ""
        self.program_type = ""
        self.program_url = ""
        self.project_type = ""
        self.project_url = ""
        self.project_description = ""
        self.name = ""
        self.short_name = ""
        self.payment_required = ""
        self.verification_datetime = ""
        self.investigator_name = ""
        self.investigator_affiliation = ""
        self.comment = "" # collapses intended_use and other descriptions
        self.description = ""
        self.support_source = ""
        self.source_url = ""
        self.citation = ""
        self.domain = ""
        self.has_api = ""
        self.has_visualization_tool = ""
        self.is_citizen_collected = ""
        self.license_type = ""
        self.license_text = ""
        self.resource_use_agreement = ""
        self.resource_contact = ""
        self.resource_id = ""
        self.resource_url = ""
        self.measures = [] # convert to tags/filters
        self.exposure_media = [] # convert to tags/filters
        self.tool_type = "" # tags/filters?
        self.type = ""


class Tag:
    """
    Tag struct in discovery metadata
    """

    def __init__(self):
        self.name = ""
        self.category = ""


class AdvSearchFilter:
    """
    advSearchFilters struct for discovery metadata
    """

    def __init__(self):
        self.key = ""
        self.value = ""


class PcorPopDataResourceModel:
    """
    Represents a pop data resource subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = ""
        self.project_id = ""
        self.project_submitter_id = ""
        self.resource_id = ""
        self.resource_submitter_id = ""
        self.created_datetime = ""
        self.state = ""
        self.updated_datetime = ""
        self.comments = ""
        self.intended_use = ""
        self.source_name = ""
        self.source_url = ""
        self.update_frequency = ""
        self.includes_citizen_collected = ""
        self.has_api = "false"
        self.has_visualization_tool = "false"
        self.time_extent_start = ""
        self.time_extent_end = ""
        self.times_available_comment = ""
        self.spatial_resolution = ""
        self.spatial_coverage = ""
        self.spatial_bounding_box = ""
        self.geometry_type = ""
        self.geometry_source = ""
        self.population = []
        self.vulnerable_population = []
        self.exposures = []
        self.outcomes = []
        self.model_methods = ""


class PcorGeoToolModel:
    """
    Represents a geospatial tool resource subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = ""
        self.project_id = ""
        self.project_submitter_id = ""
        self.resource_id = ""
        self.resource_submitter_id = ""
        self.created_datetime = ""
        self.submitter_id = ""
        self.updated_datetime = ""
        self.tool_type = []
        self.usage_type = ""
        self.operating_system = []
        self.languages = []
        self.input_formats = []
        self.output_formats = []
        self.time_extent_start = ""
        self.time_extent_end = ""
        self.times_available_comment = ""
        self.temporal_resolution = ""
        self.spatial_resolution = ""
        self.spatial_coverage = ""
        self.spatial_bounding_box = ""
        self.geometry_type = ""
        self.geometry_source = ""
        self.model_methods = ""








