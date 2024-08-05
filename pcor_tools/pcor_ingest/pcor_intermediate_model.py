import logging

ENV_CONFIG_LOCATION = 'PCOR_GEN3_CONFIG_LOCATION'

logger = logging.getLogger(__name__)


class MeasuresArrays:
    """
    contains a set of measures and the associated rollups
    """

    def __init__(self):
        self.measures = []
        self.measures_subcategories_major = []
        self.measures_subcategories_minor = []
        self.measures_parents = []


class PcorIntermediateProgramModel:
    """
    Represents a program
    """

    def __init__(self):
        self.id = None
        self.name = None
        self.dbgap_accession_number = None


class PcorSubmissionInfoModel:
    """
    Represents administrative information about a template (source, curator info and email)
    """

    def __init__(self):
        self.curator_name = ""
        self.curator_email = ""
        self.curation_comment = ""
        self.template_source = ""
        self.submit_location = ""
        self.submit_final_location = ""


class PcorIntermediateProjectModel:

    def __init__(self):
        self.program = None
        self.program_id = ""
        # project
        self.id = ""
        self.name = ""
        self.short_name = ""
        self.long_name = ""
        self.submitter_id = ""
        self.project_sponsor = []
        self.project_sponsor_type = []
        self.project_url = ""
        self.description = ""
        self.code = ""
        self.availability_mechanism = ""
        self.availability_type = ""
        self.complete = ""
        self.date_collected = ""
        self.dbgap_accession_number = ""


class PcorIntermediateResourceModel:
    """
    Represents an intermediate data model from some source (e.g. spreadsheet or CEDAR) that is to be ingested into Gen3
    This allows introduction of new curation tools that will follow the same pipeline on the Gen3 side
    """

    def __init__(self):
        self.project = ""
        # resource
        self.id = ""
        self.submitter_id = ""
        self.name = ""
        self.short_name = ""
        self.long_name = ""
        self.resource_type = ""
        self.resource_url = ""
        self.description = ""
        self.domain = []
        self.keywords = "" # collapsed to commas
        self.access_type = []
        self.payment_required = ""
        self.created_datetime = ""
        self.updated_datetime = ""
        self.verification_datetime = ""
        self.resource_reference = ""
        self.resource_use_agreement = ""
        self.publications = []
        self.is_static = ""
        self.strengths = ""
        self.limitations = ""
        self.example_applications = ""
        self.tools_supporting_uses = ""


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
        # data resc props are common
        self.display_type = ""
        self.comments = ""
        self.intended_use = ""
        self.source_name = ""
        self.update_frequency = ""
        self.includes_citizen_collected = False
        self.has_api = False
        self.has_visualization_tool = False

        # additional properties to describe the dataset
        self.data_formats = []
        self.data_location = []
        self.measures_parent = []
        self.measures_subcategory_major = []
        self.measures_subcategory_minor = []
        self.measures = []
        self.measurement_method = []
        self.time_extent_start_yyyy = None
        self.time_extent_end_yyyy = None
        self.time_available_comment = ""
        self.temporal_resolution = []
        self.spatial_resolution = ""
        self.spatial_coverage = ""
        self.spatial_coverage_specific_regions = ""
        self.spatial_bounding_box = ""
        self.geometry_type = []
        self.geometry_source = []
        self.model_methods = []
        self.exposure_media = []
        self.geographic_feature = []
        self.project_id = ""
        self.project_submitter_id = ""
        self.resource_submitter_id = ""


class PcorDiscoveryMetadata:
    """
    Represents data for Discovery presentation of a resource
    """

    def __init__(self):
        self.tags = []
        self.adv_search_filters = []
        self.program_name = ""
        self.project_sponsor = ""
        self.project_sponsor_type = ""
        self.project_name = ""
        self.project_short_name = ""
        self.project_url = ""
        self.project_description = ""
        self.name = ""
        self.payment_required = ""
        self.verification_datetime = ""
        self.comment = ""  # collapses intended_use and other descriptions
        self.description = ""
        self.update_frequency = ""
        self.resource_id = ""
        self.resource_url = ""
        self.type = ""
        self.domain = []
        self.publications = []
        self.publications_1 = ""
        self.publications_2 = ""
        self.publications_3 = ""
        self.access_type = ""
        self.resource_reference_1 = ""
        self.resource_reference_2 = ""
        self.has_api = ""
        self.has_visualization_tool = ""
        self.is_citizen_collected = ""
        self.resource_use_agreement = ""
        self.data_location_1 = ""
        self.data_location_2 = ""
        self.data_location_3 = ""
        self.variables = []
        self.data_formats = []
        self.tool_type = []
        self.source_name = ""
        self.spatial_coverage = []
        self.geometry_type = []
        self.spatial_resolution = ""
        self.time_extent_start_yyyy = None
        self.time_extent_end_yyyy = None
        self.time_available_comment = ""
        self.temporal_resolution = ""
        self.exposure_media = []
        self.measures_parent = []
        self.measures_subcategory_major = []
        self.measures_subcategory_major = []
        self.measures = []


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
        self.display_type = ""
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
        self.update_frequency = ""
        self.includes_citizen_collected = False
        self.has_api = False
        self.has_visualization_tool = False
        self.time_extent_start_yyyy = None
        self.time_extent_end_yyyy = None
        self.time_available_comment = ""
        self.spatial_resolution = ""
        self.spatial_coverage = ""
        self.temporal_resolution = []
        self.spatial_coverage_specific_regions = []
        self.geometry_type = []
        self.geometry_source = []
        self.vulnerable_population = []
        self.exposures = []
        self.outcomes = []
        self.model_methods = []
        self.population_studied = []
        self.exposure_media = []
        self.measures_parent = []
        self.measures_subcategory_major = []
        self.measures_subcategory_major = []
        self.measures = []
        self.data_formats = []
        self.data_location = []


class PcorGeoToolModel:
    """
    Represents a geospatial tool resource subtype
    """

    def __init__(self):
        self.display_type = ""
        self.pcor_intermediate_resource_model = None
        self.submitter_id = ""
        self.project_id = ""
        self.project_submitter_id = ""
        self.resource_id = ""
        self.resource_submitter_id = ""
        self.created_datetime = ""
        self.updated_datetime = ""
        self.tool_type = []
        self.intended_use = ""
        self.operating_system = []
        self.languages = []
        self.license_type = []
        self.is_open = False
        self.suggested_audience = []


class PcorKeyDatasetModel:
    """
    Represents a key dataset subtype
    """

    def __init__(self):
        self.pcor_intermediate_resource_model = None
        self.resource_id = ""
        self.resource_submitter_id = ""
        self.created_datetime = ""
        self.submitter_id = ""
        self.updated_datetime = ""
        self.display_type = ""
        self.comments = ""
        self.measures_parent = []
        self.measures_subcategory_major = []
        self.measures_subcategory_minor = []
        self.measures = []
        self.time_extent_start_yyyy = None
        self.time_extent_end_yyyy = None
        self.time_available_comment = ""
        self.temporal_resolution = ""
        self.spatial_resolution = ""
        self.spatial_coverage = ""
        self.geometry_type = []
        self.model_methods = []
        self.metrics_derived_from_data_set = ""
        self.data_formats = []
        self.data_location = []
        self.source_name = []



