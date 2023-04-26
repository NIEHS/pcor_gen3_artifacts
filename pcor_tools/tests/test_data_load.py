import json
import os
import logging

from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorDataLoad(TestCase):
    """
    Loads sample data set for integration testing and demos
    """

    def test_add_sample_resources(self):
        """ Sample data load with discovery metadata """

    pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())

    # pop data sources

    # AHRQ

    program = PcorProgramModel()
    program.name = 'AHRQ'
    program.dbgap_accession_number = 'AHRQ'
    program_id = pcor_ingest.create_program(program)

    project = PcorIntermediateProjectModel()
    project.name = "AHRQ-1"
    project.short_name = "AHRQ SDoH Data"
    project.project_code = "AHRQ-1"
    project.project_state = "open"
    project.project_release_date = "2023-04-25T12:15:59Z"
    project.support_source = "Agency for Healthcare Research and Quality"
    project.support_id = "AHRQ"
    project.releasable = "true"
    project.investigator_name = "Agency for Healthcare Research and Quality"
    project.investigator_affiliation = "Agency for Healthcare Research and Quality"
    project.dbgap_accession_number = "AHRQ-1"
    project.date_collected = "2021-1-01T00:00:00Z"
    project.complete = "Complete"
    project.availability_type = "Open"
    project_id = pcor_ingest.create_project("AHRQ", project)
    logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

    resource = PcorIntermediateResourceModel()
    resource.submitter_id = "AHRQ-AHRQ-1"
    resource.name = "AHRQ Social Determinants of Health Database"
    resource.short_name = "AHRQ SDoH"
    resource.resource_type = "data_resource"
    resource.description = "The purpose of this project is to create easy to use, easily linkable SDOH-focused data to use in PCOR research, inform approaches to address emerging health issues, and ultimately contribute to improved health outcomes. These SDOH beta data files are curated from existing Federal datasets and other publicly available data sources. The purpose of the files is to make it easier to find a range of well documented, readily linkable SDOH variables across domains without having to access multiple source files, facilitating SDOH research and analysis."
    resource.intended_use = "The database was developed to make it easier to find a range of well documented, readily linkable SDOH variables across domains without having to access multiple source files, facilitating SDOH research and analysis."
    resource.citation = "Internet Citation: Social Determinants of Health Database. Content last reviewed November 2022. Agency for Healthcare Research and Quality, Rockville, MD.        https://www.ahrq.gov/sdoh/data-analytics/sdoh-data.html      "
    resource.is_citizen_collected = "false"
    resource.has_api = "false"
    resource.domain = "social determinants of health"
    resource.keywords = ["social determinants of health", "demographic", "economic", "social", "education"]
    resource.license_type = ""
    resource.license_text = ""
    resource.created_datetime = "2023-04-25T12:15:59Z"
    resource.update_frequency = "unknown"
    resource.contact = "SDOH@ahrq.hhs.gov"
    resource.use_agreement = "false"
    resource_submit_status = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)

    pop_data_resource = PcorPopDataResourceModel()
    pop_data_resource.submitter_id = "AHRQ-AHRQ-1-POP-1"
    pop_data_resource.resource_submitter_id = resource.submitter_id
    pop_data_resource.resource_id = resource.id
    pop_data_resource.spatial_coverage = "national"
    pop_data_resource.spatial_resolution = "census_tract"
    pop_data_resource.population = ["general"]
    pop_data_resource.exposures.append("social")
    pop_data_resource.exposures.append("economic")
    pop_data_resource.exposures.append("education")
    pop_data_resource.exposures.append("infrastructure")
    pop_data_resource.exposures.append("healthcare")

    pop_data_resource.outcomes.append("")
    pop_data_resource.resource_link = "https://www.ahrq.gov/sdoh/data-analytics/sdoh-data.html"
    actual = pcor_ingest.create_pop_data_resource(program_name=program.name,
                                                  project_name=project.name,
                                                  pop_data_resource=pop_data_resource)

    # now decorate with metadata

    discovery_data = pcor_ingest.create_discovery_from_resource(program.name, project, resource)
    discovery_data.resource_url = pop_data_resource.resource_link
    pcor_ingest.decorate_resc_with_discovery(discovery_data)

    # geospatial tool

    # EPA

    program = PcorProgramModel()
    program.name = 'EPA'
    program.dbgap_accession_number = 'EPA'
    program_id = pcor_ingest.create_program(program)

    project = PcorIntermediateProjectModel()
    project.name = "EPA-1"
    project.short_name = "EJSCREEN"
    project.project_code = "EPA-1"
    project.project_state = "open"
    project.project_release_date = "2023-04-25T12:15:59Z"
    project.support_source = "EJScreen: Environmental Justice Screening and Mapping Tool"
    project.support_id = "EPA"
    project.releasable = "true"
    project.investigator_name = "U.S. Environmental Protection Agency"
    project.investigator_affiliation = "U.S. Environmental Protection Agency"
    project.dbgap_accession_number = "EPA-1"
    project.date_collected = "2021-1-01T00:00:00Z"
    project.complete = "Complete"
    project.availability_type = "Open"
    project_id = pcor_ingest.create_project("EPA", project)
    logger.info('Project name: %s is associated with id: %s' % (project.name, project_id))

    resource = PcorIntermediateResourceModel()
    resource.submitter_id = "EPA-EPA-1"
    resource.name = "EJScreen: Environmental Justice Screening and Mapping Tool"
    resource.short_name = "EJScreen"
    resource.resource_type = "tool_resource"
    resource.description = "In order to better meet the Agency’s responsibilities related to the protection of public health and the environment, EPA has developed a new environmental justice (EJ) mapping and screening tool called EJScreen. It is based on nationally consistent data and an approach that combines environmental and demographic indicators in maps and reports. "
    resource.intended_use = "Screening tools should be used for a 'screening-level' look. Screening is a useful first step in understanding or highlighting locations that may be candidates for further review."
    resource.citation = ""
    resource.is_citizen_collected = "false"
    resource.has_api = "true"
    resource.domain = "exposures"
    resource.keywords = ["air quality", "lead paint", "superfund", "hazardous waste", "wastewater discharge"]
    resource.license_type = ""
    resource.license_text = ""
    resource.created_datetime = "2023-04-25T12:15:59Z"
    resource.update_frequency = "unknown"
    resource.contact = "https://www.epa.gov/ejscreen/forms/contact-us-about-ejscreen"
    resource.use_agreement = "false"
    resource_submit_status = pcor_ingest.create_resource(program.name, project.dbgap_accession_number, resource)

    geo_tool_resource = PcorGeoToolModel()
    geo_tool_resource.submitter_id = "EPA-EPA-1-TOOL-1"
    geo_tool_resource.resource_link = "https://www.epa.gov/ejscreen"
    geo_tool_resource.resource_id = resource.id
    geo_tool_resource.resource_submitter_id = resource.submitter_id
    geo_tool_resource.tool_type = "service"
    geo_tool_resource.input_format = ""
    geo_tool_resource.output_format = "report"
    geo_tool_resource.language = "Other"
    geo_tool_resource.is_open_source = "false"
    geo_tool_resource.temporal_resolution = "fixed"
    geo_tool_resource.geometry_type = "census tract"
    geo_tool_resource.geo_ref_system = ""
    geo_tool_resource.spatial_resolution = "census_tract"
    geo_tool_resource.spatial_coverage = "national"

    # using result from resource creation status
    geo_tool_resource.resource_id = resource_submit_status.id
    geo_tool_resource.resource_submitter_id = resource.submitter_id

    actual = pcor_ingest.create_geo_spatial_tool_resource(program_name=program.name,
                                                  project_name=project.name,
                                                  geo_spatial_tool_resource=geo_tool_resource)

    # now decorate with metadata

    discovery_data = pcor_ingest.create_discovery_from_resource(program.name, project, resource)
    discovery_data.resource_url = geo_tool_resource.resource_link
    pcor_ingest.decorate_resc_with_discovery(discovery_data)

