import os
import logging

ENV_CONFIG_LOCATION = 'PCOR_GEN3_CONFIG_LOCATION'

logger = logging.getLogger(__name__)


class PcorIntermediateProjectModel:

    def __int__(self):
        self.program = None
        # project
        self.program_id = None
        self.id = None
        self.name = None
        self.availability_mechanism = None
        self.availability_type = None
        self.dbgap_accession_number = None
        self.date_collected = None
        self.submitter_id
        self.project_name = None
        self.project_release_date = None
        self.investigator_affiliation = None
        self.investigator_name = None
        self.releasable = False
        self.released = False
        self.support_source = None
        self.support_id = None
        self.project_state = 'open'
        self.project_type = None
        self.project_code = None
        self.complete = None


class PcorIntermediateResourceModel:
    """
    Represents an intermediate data model from some source (e.g. spreadsheet or CEDAR) that is to be ingested into Gen3
    This allows introduction of new curation tools that will follow the same pipeline on the Gen3 side
    """

    def __int__(self):

        self.intermediate_project_model = None
        # resource
        self.resource_submitter_id = None
        self.created_datetime = None
        self.resource_id = None
        self.resource_name = None
        self.resource_secondary_name = None
        self.resource_type = None
        self.resource_description = None
        self.resource_subject = None
        self.resource_keywords = []
        self.update_frequencey = 'unknown'
        self.license_type = None
        self.license_text = None
        self.verification_datetime = None
        self.resource_use_agreement = None
        self.resource_contact = None


class PcorGeospatialDataResourceModel:
    """
    Represents a geospatial data resource subtype
    """

    def __int__(self):
        self.pcor_intermediate_resource_model = None
        self.submitter_id = None
        self.project_id = None
        self.project_submitter_id = None
        self.resource_id = None
        self.resource.submitter_id = None
        self.created_datetime = None
        self.state = None
        self.submitter_id = None
        self.updated_datetime = None
        self.observation = None
        self.time_extent_start = None
        self.time_extent_end = None
        self.time_points = [] # make array in model
        self.spatial_resolution = None
        self.spatial_coverage = None
        self.resource_link = None








