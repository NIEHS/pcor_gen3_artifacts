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
from pcor_ingest.measures_rollup import PcorMeasuresRollup

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

    def __init__(self, pcor_ingest_configuration):
        self.cedar_config = CedarConfig()
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.pcor_measures_rollup = PcorMeasuresRollup(self.pcor_ingest_configuration.measures_rollup)

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

            # add the measures rollup
            measures_rollup = self.pcor_measures_rollup.process_measures(geospatial_data_resource.measures)
            geospatial_data_resource.measures_parent = measures_rollup.measures_parents
            geospatial_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            geospatial_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor

            geospatial_data_resource.model_methods.extend(geospatial_data_resource.model_methods_other)
            geospatial_data_resource.spatial_coverage.extend(geospatial_data_resource.spatial_coverage_other)
            geospatial_data_resource.spatial_resolution.extend(geospatial_data_resource.spatial_resolution_other)
            geospatial_data_resource.temporal_resolution.extend(geospatial_data_resource.temporal_resolution_other)


        population_data_resource = data_model.get("population_data_resource", None)
        if population_data_resource:
            logger.info("processing population data resource %s" % population_data_resource)

            if population_data_resource.update_frequency_other:
                population_data_resource.update_frequency.append(population_data_resource.update_frequency_other)
            population_data_resource.geometry_source.extend(
                population_data_resource.geometry_source_other)
            population_data_resource.measures.extend(
                population_data_resource.measures_other)
            population_data_resource.model_methods.extend(population_data_resource.model_methods_other)
            population_data_resource.spatial_coverage.extend(population_data_resource.spatial_coverage_other)
            population_data_resource.spatial_resolution.extend(population_data_resource.spatial_resolution_other)
            population_data_resource.temporal_resolution.extend(population_data_resource.temporal_resolution_other)

        geo_tool_resource = data_model.get("geospatial_tool_resource", None)
        if geo_tool_resource:
            logger.info("processing geospatial tool resource %s" % geo_tool_resource)
            geo_tool_resource.languages.extend(geo_tool_resource.languages_other)
            geo_tool_resource.license_type.extend(geo_tool_resource.license_type_other)
            geo_tool_resource.operating_system.extend(geo_tool_resource.operating_system_other)
            geo_tool_resource.tool_type.extend(geo_tool_resource.tool_type_other)

        key_data_resource = data_model.get("key_dataset", None)
        if key_data_resource:
            logger.info("processing key data resource %s" % key_data_resource)
            if key_data_resource.update_frequency_other:
                key_data_resource.update_frequency.append(key_data_resource.update_frequency_other)
            key_data_resource.geographic_feature.extend(
                key_data_resource.geographic_feature_other)
            key_data_resource.geometry_source.extend(
                key_data_resource.geometry_source_other)
            key_data_resource.license_type.extend(key_data_resource.license_type_other)
            key_data_resource.measurement_method.extend(key_data_resource.measurement_method_other)
            key_data_resource.measures.extend(
                key_data_resource.measures_other)

            # add the measures rollup
            measures_rollup = self.pcor_measures_rollup.process_measures(key_data_resource.measures)
            key_data_resource.measures_parent = measures_rollup.measures_parents
            key_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            key_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor

            key_data_resource.model_methods.extend(key_data_resource.model_methods_other)
            key_data_resource.spatial_coverage.extend(key_data_resource.spatial_coverage_other)
            key_data_resource.spatial_resolution.extend(key_data_resource.spatial_resolution_other)
            key_data_resource.spatial_resolution_all_available.extend(
                key_data_resource.spatial_resolution_all_other_available)
            key_data_resource.temporal_resolution.extend(key_data_resource.temporal_resolution_other)
            key_data_resource.temporal_resolution_all_available.extend(
                key_data_resource.temporal_resolution_all_other_available)
            key_data_resource.use_suggested.extend(
                key_data_resource.use_suggested_other)