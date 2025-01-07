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

        # Helper function to extend attributes and remove 'other'
        def extend_and_remove_other(obj, attributes):
            for attr, other_attr in attributes:
                primary_list = getattr(obj, attr, None)
                other_list = getattr(obj, other_attr, None)
                if primary_list is not None and other_list is not None:
                    primary_list.extend(other_list)
                    # Remove 'other/Other' if it exists in the primary list
                    if 'other' in primary_list:
                        primary_list.remove('other')
                    if 'Other' in primary_list:
                        primary_list.remove('Other')

        # collapse project other
        project = data_model.get("project", None)
        logger.info("processing project %s" % data_model.get("project"))
        extend_and_remove_other(project, [
            ("project_sponsor", "project_sponsor_other"),
            ("project_sponsor_type", "project_sponsor_type_other")
        ])

        # collapse resource props
        resource = data_model.get("resource", None)
        logger.info("processing resource %s" % data_model.get("resource"))
        extend_and_remove_other(resource, [
            ("domain", "domain_other")
        ])

        # collapse geo data props
        geospatial_data_resource = data_model.get("geospatial_data_resource", None)
        if geospatial_data_resource:
            logger.info("processing geospatial data resource %s" % geospatial_data_resource)

            # List of attribute pairs to extend
            extend_and_remove_other(geospatial_data_resource, [
                ("geographic_feature", "geographic_feature_other"),
                ("geometry_source", "geometry_source_other"),
                ("measurement_method", "measurement_method_other"),
                ("measures", "measures_other"),
                ("model_methods", "model_methods_other"),
                ("spatial_coverage", "spatial_coverage_other"),
                ("spatial_resolution", "spatial_resolution_other"),
                ("temporal_resolution", "temporal_resolution_other")
            ])

            # Add the measures rollup
            measures_rollup = self.pcor_measures_rollup.process_measures(geospatial_data_resource.measures)
            geospatial_data_resource.measures_parent = measures_rollup.measures_parents
            geospatial_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            geospatial_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor

        # collapse pop data props
        population_data_resource = data_model.get("population_data_resource", None)
        if population_data_resource:
            logger.info("processing population data resource %s" % population_data_resource)

            if population_data_resource.update_frequency_other:
                population_data_resource.update_frequency.append(population_data_resource.update_frequency_other)
            extend_and_remove_other(population_data_resource, [
                ("geometry_source", "geometry_source_other"),
                ("measures", "measures_other"),
                ("model_methods", "model_methods_other"),
                ("spatial_coverage", "spatial_coverage_other"),
                ("spatial_resolution", "spatial_resolution_other"),
                ("temporal_resolution", "temporal_resolution_other")
            ])

        # collapse geo tool props
        geo_tool_resource = data_model.get("geospatial_tool_resource", None)
        if geo_tool_resource:
            logger.info("processing geospatial tool resource %s" % geo_tool_resource)
            extend_and_remove_other(geo_tool_resource, [
                ("languages", "languages_other"),
                ("license_type", "license_type_other"),
                ("operating_system", "operating_system_other"),
                ("tool_type", "tool_type_other")
            ])

        # collapse key data props
        key_data_resource = data_model.get("key_dataset", None)
        if key_data_resource:
            logger.info("processing key data resource %s" % key_data_resource)
            if key_data_resource.update_frequency_other:
                key_data_resource.update_frequency.append(key_data_resource.update_frequency_other)
                extend_and_remove_other(key_data_resource, [
                    ("geographic_feature", "geographic_feature_other"),
                    ("geometry_source", "geometry_source_other"),
                    ("license_type", "license_type_other"),
                    ("measurement_method", "measurement_method_other"),
                    ("measures", "measures_other"),
                    ("model_methods", "model_methods_other"),
                    ("spatial_coverage", "spatial_coverage_other"),
                    ("spatial_resolution", "spatial_resolution_other"),
                    ("spatial_resolution_all_available", "spatial_resolution_all_other_available"),
                    ("temporal_resolution", "temporal_resolution_other"),
                    ("temporal_resolution_all_available", "temporal_resolution_all_other_available"),
                    ("use_suggested", "use_suggested_other")
                ])

            # add the measures rollup
            measures_rollup = self.pcor_measures_rollup.process_measures(key_data_resource.measures)
            key_data_resource.measures_parent = measures_rollup.measures_parents
            key_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            key_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor


