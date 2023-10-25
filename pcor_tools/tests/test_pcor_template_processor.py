import logging
from unittest import TestCase

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel
from pcor_ingest.pcor_template_parser import PcorTemplateParseResult
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

# program model
program = PcorProgramModel()
program.name = 'NFS'
program.dbgap_accession_number = 'NFS'

# project model
project = PcorIntermediateProjectModel()
project.name = "NFS-2"
project.project_code = "NFS-2"
project.support_source = "support source1"
project.support_id = "support id1"
project.investigator_name = "Mike Conway"
project.investigator_affiliation = "NIEHS"
project.dbgap_accession_number = "NFS-2"
project.date_collected = "2023/01/01T12:01:00Z"
project.complete = "Complete"
project.availability_type = "Open"

# resource model
resource = PcorIntermediateResourceModel()
resource.submitter_id = "NFS-2-RESC-1"
resource.resource_id = "NFS-2-RESC-1"
resource.name = "Fire and Smoke Map"
resource.short_name = "short name"
resource.resource_type = "data_resource"
resource.description = "description"
resource.intended_use = "intended use"
resource.citation = "citation"
resource.is_citizen_collected = "false"
resource.has_api = "false"
resource.domain = "AQI - Air Quality Index"
resource.keywords = ["fire", "smoke", "aqi", "wildfire"]
resource.license_type = ""
resource.license_text = ""
resource.created_datetime = ""
resource.update_frequency = "hourly"
resource.contact = "USFS - contact firesmokemap@epa.gov"
resource.use_agreement = "false"

# geo_spatial_resource model
geo_spatial_resource = PcorGeospatialDataResourceModel()
geo_spatial_resource.submitter_id = "NFS-2-GEO-1"
geo_spatial_resource.resource_link = "https://landfire.gov/"
geo_spatial_resource.spatial_coverage = "national"
geo_spatial_resource.spatial_resolution = "10km"
geo_spatial_resource.temporal_resolution = "unknown"
geo_spatial_resource.is_modeled = "false"

# pop_data_resource model
pop_data_resource = PcorPopDataResourceModel()
pop_data_resource.submitter_id = "NFS-2-POP-1"
pop_data_resource.spatial_coverage = "national"
pop_data_resource.spatial_resolution = "10km"
pop_data_resource.population = ["wildland/urban interface"]
pop_data_resource.exposures.append("toxic smoke")
pop_data_resource.outcomes.append("asthma")
pop_data_resource.resource_link = "https://landfire.gov/"

# geo_tool_resource model
geo_tool_resource = PcorGeoToolModel()
geo_tool_resource.submitter_id = "NOAA-1-GEOTOOL-1"
geo_tool_resource.resource_link = "https://a.tool.gov/"
geo_tool_resource.spatial_coverage = "national"
geo_tool_resource.spatial_resolution = "10km"
geo_tool_resource.temporal_resolution = "unknown"
geo_tool_resource.is_open_source = "false"
geo_tool_resource.tool_type = "software"
geo_tool_resource.operating_system.append("linux")
geo_tool_resource.language = "Go"
geo_tool_resource.input_format = "Net/CDF"
geo_tool_resource.output_format = "binary"


class TestPcorTemplateProcessor(TestCase):
    def test_process_add_program(self):
        logger.info('test_process_add_program')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        process_template.process(parsed_data=parsed_data)

    def test_process_add_project(self):
        logger.info('test_process_add_project')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        parsed_data.model_data["project"] = project
        process_template.process(parsed_data=parsed_data)

    def test_process_add_resource(self):
        logger.info('test_process_add_resource')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        parsed_data.model_data["project"] = project
        parsed_data.model_data["resource"] = resource
        process_template.process(parsed_data=parsed_data)

    def test_process_add_geo_spatial_resource(self):
        logger.info('test_process_add_geo_spatial_resource')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        parsed_data.model_data["project"] = project
        parsed_data.model_data["resource"] = resource
        parsed_data.model_data["geo_spatial_resource"] = geo_spatial_resource
        process_template.process(parsed_data=parsed_data)

    def test_process_add_pop_data_resource(self):
        logger.info('test_process_add_pop_data_resource')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        parsed_data.model_data["project"] = project
        parsed_data.model_data["resource"] = resource
        parsed_data.model_data["pop_data_resource"] = pop_data_resource
        process_template.process(parsed_data=parsed_data)

    def test_process_add_geo_tool_resource(self):
        logger.info('test_process_add_geo_tool_resource')
        process_template = PcorTemplateProcessor()
        parsed_data = PcorTemplateParseResult()
        parsed_data.model_data["program"] = program
        parsed_data.model_data["project"] = project
        parsed_data.model_data["resource"] = resource
        parsed_data.model_data["geo_tool_resource"] = geo_tool_resource
        process_template.process(parsed_data=parsed_data)
