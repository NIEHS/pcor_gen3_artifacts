import json
import os
import logging

from unittest import TestCase
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from tests import pcor_testing_utilities
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel,  PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel

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

        # ---------------------------------------------
        # NFS 1

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NFS"
        project = PcorIntermediateProjectModel()
        project.project_name = "NFS-1"
        project.project_code = "NFS-1"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = ""
        project.support_id = ""
        project.releasable = True
        project.investigator_name = "Mike Conway"
        project.investigator_affiliation = "NFS"
        project.dbgap_accession_number = "NFS-1"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NFS", project)
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NFS-1-1"
        resource.resource_id = "NFS-1-1"
        resource.name = "AirNow"
        resource.resource_type = "data_resource"
        resource.subject = "AQI - Air Quality Index"
        resource.keywords = ["fire", "smoke", "wildfire"]
        resource.update_frequency = "hourly"
        resource.secondary_name = "AirNow Plume Mapping"
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "NFS - contact firesmokemap@epa.gov"
        resource.description = """The AirNow Fire and Smoke Map provides information that you can use to help protect your health from wildfire smoke. Use this map to see Current particle pollution air quality information for your location; Fire locations and smoke plumes; Smoke Forecast Outlooks, where available; and,Recommendations for actions to take to protect yourself from smoke. These recommendations were developed by EPA scientists who are experts in air quality and health. The Map is a collaborative effort between the U.S. Forest Service (USFS)-led Interagency Wildland Fire Air Quality Response Program and the U.S. Environmental Protection Agency (EPA)."""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        resc_id = actual.id

        geo_spatial_resource = PcorGeospatialDataResourceModel()
        geo_spatial_resource.submitter_id = "NFS-1-1-1"
        geo_spatial_resource.resource_submitter_id = resource.submitter_id
        geo_spatial_resource.observation = "wildfire_plume"
        geo_spatial_resource.resource_link = "https://fire.airnow.gov/"
        geo_spatial_resource.spatial_coverage = "national"
        geo_spatial_resource.spatial_resolution = "10km"

        # using result from resource creation status
        geo_spatial_resource.resource_id = resc_id

        actual = pcor_ingest.create_geo_spatial_data_resource(program_name=program,
                                                              project_name=project.project_name,
                                                              geo_spatial_data_resource=geo_spatial_resource)

        # now add the discovery data
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "web site"
        tag.category = "Link Type"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "NFS"
        tag.category = "Program"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "smoke plume"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "geospatial data resource"
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        for kw in resource.keywords:
            tag = Tag()
            tag.name = kw
            tag.category = "Keyword"
            discovery.tags.append(tag)

        discovery.name = resource.name
        discovery.type = resource.resource_type
        discovery.resource_url = geo_spatial_resource.resource_link
        discovery.resource_id = resc_id
        discovery.full_name = resource.name
        discovery.description = resource.description
        discovery.subject = resource.subject

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = "geospatial data resource"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = "NFS"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Subject"
        filter.value = "smoke"
        discovery.adv_search_filters.append(filter)

        pcor_ingest.decorate_resc_with_discovery(discovery)

        # ---------------------------------------------
        # NOAA 1

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "NOAA"
        project = PcorIntermediateProjectModel()
        project.project_name = "NOAA-1"
        project.project_code = "NOAA-1"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = ""
        project.support_id = ""
        project.releasable = True
        project.investigator_name = "Wilfrid Schroeder"
        project.investigator_affiliation = "NOAA"
        project.dbgap_accession_number = "NOAA-1"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("NOAA", project)
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "NOAA-1-1"
        resource.resource_id = "NOAA-1-1"
        resource.name = "Hazard Mapping System Fire and Smoke Product"
        resource.resource_type = "data_resource"
        resource.subject = "Smoke"
        resource.keywords = ["fire", "smoke", "wildfire"]
        resource.update_frequency = "continuous"
        resource.secondary_name = "Office of Satellite and Product Operations"
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "SPSD.Userservices@noaa.gov"
        resource.description = """To disseminate satellite derived, quality controlled information on active fires and the extent of smoke plumes. JPEG and text since early 2000s, GIS since 2005, KML since 2009, WFS since 2021"""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        resc_id = actual.id

        geo_spatial_resource = PcorGeospatialDataResourceModel()
        geo_spatial_resource.submitter_id = "NOAA-1-1-1"
        geo_spatial_resource.resource_submitter_id = resource.submitter_id
        geo_spatial_resource.observation = "wildfire_plume"
        geo_spatial_resource.resource_link = "https://www.ospo.noaa.gov/Products/land/hms.html#maps"
        geo_spatial_resource.spatial_coverage = "national"
        geo_spatial_resource.spatial_resolution = "10km"

        # using result from resource creation status
        geo_spatial_resource.resource_id = resc_id

        actual = pcor_ingest.create_geo_spatial_data_resource(program_name=program,
                                                              project_name=project.project_name,
                                                              geo_spatial_data_resource=geo_spatial_resource)

        # now add the discovery data
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "web site"
        tag.category = "Link Type"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = program
        tag.category = "Program"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "smoke"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "fire"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "geospatial data resource"
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        for kw in resource.keywords:
            tag = Tag()
            tag.name = kw
            tag.category = "Keyword"
            discovery.tags.append(tag)

        discovery.name = resource.name
        discovery.type = resource.resource_type
        discovery.resource_url = geo_spatial_resource.resource_link
        discovery.resource_id = resc_id
        discovery.full_name = resource.name
        discovery.description = resource.description
        discovery.subject = resource.subject

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = "geospatial data resource"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = program
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Subject"
        filter.value = resource.subject
        discovery.adv_search_filters.append(filter)

        pcor_ingest.decorate_resc_with_discovery(discovery)

        # ---------------------------------------------
        # EPA 1

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "EPA"
        project = PcorIntermediateProjectModel()
        project.project_name = "EPA-1"
        project.project_code = "EPA-1"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = ""
        project.support_id = ""
        project.releasable = True
        project.investigator_name = "EPA Office of Environmental Justice"
        project.investigator_affiliation = "EPA"
        project.dbgap_accession_number = "EPA-1"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("EPA", project)
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "EPA-1-1"
        resource.resource_id = "EPA-1-1"
        resource.name = "EJSCREEN"
        resource.resource_type = "data_resource"
        resource.subject = "Environmental Justice"
        resource.keywords = ["environmental justice", "population"]
        resource.update_frequency = "unknown"
        resource.secondary_name = " Environmental Justice Screening and Mapping Tool"
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "https://www.epa.gov/ejscreen/forms/contact-us-about-ejscreen"
        resource.description = """Environmental justice screening and mapping tool"""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        resc_id = actual.id

        pop_data_resource = PcorPopDataResourceModel()
        pop_data_resource.submitter_id = "EPA-1-1"
        pop_data_resource.spatial_coverage = "national"
        pop_data_resource.spatial_resolution = "census_tract"
        pop_data_resource.population = ["general"]
        pop_data_resource.exposure = "environmental and socioeconomic"
        pop_data_resource.resource_link = "https://www.epa.gov/ejscreen"

        # using result from resource creation status
        pop_data_resource.resource_submitter_id = resource.submitter_id
        pop_data_resource.project_submitter_id = project.dbgap_accession_number

        pop_resc_id = pcor_ingest.create_pop_data_resource(program_name=program,
                                                      project_name=project.project_name,
                                                      pop_data_resource=pop_data_resource)

        # now add the discovery data
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "web site"
        tag.category = "Link Type"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = program
        tag.category = "Program"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "socioeconomic indicators"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "environmental exposures"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "population data resource"
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        for kw in resource.keywords:
            tag = Tag()
            tag.name = kw
            tag.category = "Keyword"
            discovery.tags.append(tag)

        discovery.name = resource.name
        discovery.type = resource.resource_type
        discovery.resource_url = pop_data_resource.resource_link
        discovery.resource_id = resc_id
        discovery.full_name = resource.name
        discovery.description = resource.description
        discovery.subject = resource.subject

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = "population data resource"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = program
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Subject"
        filter.value = resource.subject
        discovery.adv_search_filters.append(filter)

        pcor_ingest.decorate_resc_with_discovery(discovery)

    def test_add_sample_resources2(self):
        """ Sample data load with discovery metadata """

        # ---------------------------------------------
        # USGS 1

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())
        program = "USGS"
        project = PcorIntermediateProjectModel()
        project.project_name = "USGS-2"
        project.project_code = "USGS-2"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = ""
        project.support_id = ""
        project.releasable = True
        project.investigator_name = ""
        project.investigator_affiliation = "USGS"
        project.dbgap_accession_number = "USGS-2"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("USGS", project)
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "USGS-2-1"
        resource.resource_id = "USGS-2-1"
        resource.name = "USGS National Map"
        resource.resource_type = "data_resource"
        resource.subject = "Mapping"
        resource.keywords = ["map", "topography"]
        resource.update_frequency = "fixed"
        resource.secondary_name = ""
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "https://answers.usgs.gov/"
        resource.description = """Several layers available, on land cover, impervious surface, elevation, but also structures (schools, medical and emergency response facilities, transportation, etc.)"""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        resc_id = actual.id

        pop_data_resource = PcorPopDataResourceModel()
        pop_data_resource.submitter_id = "USGS-2-1"
        pop_data_resource.spatial_coverage = "national"
        pop_data_resource.spatial_resolution = "10km"
        pop_data_resource.population = ["general"]
        pop_data_resource.exposure = ""
        pop_data_resource.resource_link = "https://apps.nationalmap.gov/viewer/"

        # using result from resource creation status
        pop_data_resource.resource_submitter_id = resource.submitter_id
        pop_data_resource.project_submitter_id = project.dbgap_accession_number

        pop_resc_id = pcor_ingest.create_pop_data_resource(program_name=program,
                                                           project_name=project.project_name,
                                                           pop_data_resource=pop_data_resource)

        # now add the discovery data
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "map"
        tag.category = "Link Type"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = program
        tag.category = "Program"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "location"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "land cover"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "impervious surfaces"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "population data resource"
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        for kw in resource.keywords:
            tag = Tag()
            tag.name = kw
            tag.category = "Keyword"
            discovery.tags.append(tag)

        discovery.name = resource.name
        discovery.type = resource.resource_type
        discovery.resource_url = pop_data_resource.resource_link
        discovery.resource_id = resc_id
        discovery.full_name = resource.name
        discovery.description = resource.description
        discovery.subject = resource.subject

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = "population data resource"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = program
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Subject"
        filter.value = resource.subject
        discovery.adv_search_filters.append(filter)

        pcor_ingest.decorate_resc_with_discovery(discovery)

        # ---------------------------------------------
        # Census 1

        pcor_ingest = PcorGen3Ingest(pcor_testing_utilities.get_pcor_ingest_configuration())

        #pcor_ingest.delete_project("NFS", "Census-1")
        #pcor_ingest.delete_project("NFS", "Census-2")

        program = "Census"
        project = PcorIntermediateProjectModel()
        project.project_name = "Census-2"
        project.project_code = "Census-2"
        project.project_state = "open"
        project.project_release_date = ""
        project.support_source = ""
        project.support_id = ""
        project.releasable = True
        project.investigator_name = ""
        project.investigator_affiliation = "Census"
        project.dbgap_accession_number = "Census-2"
        project.date_collected = ""
        project.complete = "Complete"
        project.availability_type = "Open"
        project_id = pcor_ingest.create_project("Census", project)
        logger.info('Project name: %s is associated with id: %s' % (project.project_name, project_id))

        resource = PcorIntermediateResourceModel()
        resource.submitter_id = "Census-2-1"
        resource.resource_id = "Census-2-1"
        resource.name = "ACS"
        resource.resource_type = "data_resource"
        resource.subject = "Mapping"
        resource.keywords = ["map", "population", "socioeconomic", "demographic"]
        resource.update_frequency = "fixed"
        resource.secondary_name = ""
        resource.license_type = ""
        resource.license_text = ""
        resource.created_datetime = ""
        resource.contact = "https://www.census.gov/programs-surveys/acs/news/data-releases.html"
        resource.description = """American Community Survey demographic, socioeconomic and other data. Has several variables related to population distributions, specific vulnerabilities, also variables that would be useful to have for planning evacuations/emergency response etc.."""
        resource.use_agreement = "false"
        resource.verification_datetime = "null"
        actual = pcor_ingest.create_resource(program, project.dbgap_accession_number, resource)
        resc_id = actual.id

        pop_data_resource = PcorPopDataResourceModel()
        pop_data_resource.submitter_id = "Census-2-1"
        pop_data_resource.spatial_coverage = "national"
        pop_data_resource.spatial_resolution = "census_tract"
        pop_data_resource.population = ["general"]
        pop_data_resource.exposure = ""
        pop_data_resource.resource_link = "https://www.census.gov/programs-surveys/acs/news/data-releases.html"

        # using result from resource creation status
        pop_data_resource.resource_submitter_id = resource.submitter_id
        pop_data_resource.project_submitter_id = project.dbgap_accession_number

        pop_resc_id = pcor_ingest.create_pop_data_resource(program_name=program,
                                                           project_name=project.project_name,
                                                           pop_data_resource=pop_data_resource)

        # now add the discovery data
        discovery = PcorDiscoveryMetadata()
        tag = Tag()
        tag.name = "map"
        tag.category = "Link Type"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = program
        tag.category = "Program"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "location"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "socioeconomic"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "demographic"
        tag.category = "Variable"
        discovery.tags.append(tag)

        tag = Tag()
        tag.name = "population data resource"
        tag.category = "Resource Type"
        discovery.tags.append(tag)

        for kw in resource.keywords:
            tag = Tag()
            tag.name = kw
            tag.category = "Keyword"
            discovery.tags.append(tag)

        discovery.name = resource.name
        discovery.type = resource.resource_type
        discovery.resource_url = pop_data_resource.resource_link
        discovery.resource_id = resc_id
        discovery.full_name = resource.name
        discovery.description = resource.description
        discovery.subject = resource.subject

        filter = AdvSearchFilter()
        filter.key = "Resource Type"
        filter.value = "population data resource"
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Program"
        filter.value = program
        discovery.adv_search_filters.append(filter)

        filter = AdvSearchFilter()
        filter.key = "Subject"
        filter.value = resource.subject
        discovery.adv_search_filters.append(filter)

        pcor_ingest.decorate_resc_with_discovery(discovery)




