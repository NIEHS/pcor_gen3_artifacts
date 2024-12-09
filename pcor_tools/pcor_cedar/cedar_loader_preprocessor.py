import logging
import math
import re
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from gen3.cli.wss import upload_url
from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
from pcor_ingest.ingest_context import PcorIngestConfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

"""
Preprocess an intermediate data model for loading into Gen3

The purpose is to collapse 'other' fields into parent fields in the model
before presenting to the jinja templates for Gen3 load
"""
class CedarLoaderPreprocessor:

    def __init__(self):
        self.cedar_config = CedarConfig()

    def process(self, data_model):
        logger.info("process()")

        # collapse project other

        project = data_model.get("project", None)
        logger.info("processing project %s" % data_model.get("project"))
        project.project_sponsor.extend(project.project_sponsor_other)
        project.project_sponsor_type.extend(project.project_sponsor_type_other)

        resource = data_model.get("resource", None)
        logger.info("processing resource %s" % data_model.get("resource"))
        resource.domain.extend(resource.domain_other)

        geospatial_data_resource = data_model.get("geospatial_data_resource", None)

        if geospatial_data_resource:
            logger.info("processing geospatial data resource %s" % geospatial_data_resource)
            geospatial_data_resource.geographic_feature.extend(
                geospatial_data_resource.geographic_feature_other)
            geospatial_data_resource.geometry_source.extend(
                geospatial_data_resource.geometry_source_other)
            geospatial_data_resource.measurement_method.extend(
                geospatial_data_resource.measurement_method_other)
            geospatial_data_resource.measures.extend(
                geospatial_data_resource.measures_other)
            geospatial_data_resource.model_methods.extend(geospatial_data_resource.model_methods_other)
            geospatial_data_resource.spatial_coverage.extend(geospatial_data_resource.spatial_coverage_other)
            geospatial_data_resource.spatial_resolution.extend(geospatial_data_resource.spatial_resolution_other)
            geospatial_data_resource.temporal_resolution.extend(geospatial_data_resource.temporal_resolution_other)


        population_data_resource = data_model.get("population_data_resource", None)
        if population_data_resource:
            logger.info("processing population data resource %s" % population_data_resource)
            population_data_resource.update_frequency.extend(population_data_resource.update_frequency_other)
            population_data_resource.geometry_source.extend(
                population_data_resource.geometry_source_other)
            population_data_resource.measures.extend(
                population_data_resource.measures_other)
            population_data_resource.model_methods.extend(population_data_resource.model_method_other)
            population_data_resource.spatial_coverage.extend(population_data_resource.spatial_coverage_other)
            population_data_resource.spatial_resolution.extend(population_data_resource.spatial_resolution_other)
            population_data_resource.temporal_resolution.extend(population_data_resource.temporal_resolution_other)

        population_tool_resource = data_model.get("population_tool_resource", None)
        if population_tool_resource:
            logger.info("processing population tool resource %s" % population_tool_resource)
            population_tool_resource.languages.extend(population_tool_resource.languages_other)
            population_tool_resource.license_type.extend(population_tool_resource.license_type_other)
            population_tool_resource.operating_system.extend(population_tool_resource.operating_system_other)
            population_tool_resource.tool_type.extend(population_tool_resource.tool_type_other)

