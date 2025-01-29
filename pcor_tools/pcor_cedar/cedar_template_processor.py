"""
support for jinja templates -> cedar json processing
any cedar artifacts produced via jinja templates can be handled here
"""

import json
import os
import logging
import sys

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class CedarTemplateProcessor:
    """
    Library for ingesting data into PCOR
    """

    def __init__(self):
        """
        Initialize ingest tool
        :param pcor_ingest_configuration: IngestConfiguration with Gen3 server properties
        :param gen3_auth: Optional Gen3Auth object if auth is done
        :return:
        """

        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the relative path to your template directory
        template_rel_path = 'templates'

        # Construct the absolute path to the template directory
        template_dir = os.path.join(script_dir, template_rel_path)

        # Create a Jinja environment with the FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug('template_dir: %s' % template_dir)
        self.env.filters['jsonify'] = json.dumps

    def produce_rename_resource(self, id, name):
        """
        Create the call to rename a resource
        Parameters
        ----------
        id the id of the resoure
        name the new name

        Returns
        -------
        json for the api call
        """
        logger.info("processing rename resource for id: %s and name: %s" % (id, name))
        template = self.env.get_template("resource_rename.jinja")
        rendered = template.render(id = id, name = name)
        logger.info("rendered: %s" % rendered)
        return rendered


    def produce_geospatial_cedar_instance(self, model, version_tag):
        """
        Create the json that is a new resource to add to CEDAR for geospatial data
        Parameters
        ----------
        model - the dictionary as found in PcorProcessResult that feeds the template

        Returns
        -------
        string with the resource json
        """
        logger.info("produce_geospatial_cedar_instance()")
        template = self.env.get_template(f"cedar_geoexposure_resource_{version_tag}.jinja")
        rendered = (template.render(submission=model["submission"], program=model["program"], project=model["project"], resource=model["resource"],
                                    geospatial_data_resource=model["geospatial_data_resource"])
                     .replace('"none"', 'null').replace('"None"', 'null')
                     .replace('""','null'))
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_key_dataset_cedar_instance(self, model, version_tag):
        """
        Create the json that is a new resource to add to CEDAR for geospatial data
        Parameters
        ----------
        model - the dictionary as found in PcorProcessResult that feeds the template

        Returns
        -------
        string with the resource json
        """
        logger.info("produce_key_dataset_cedar_instance()")
        template = self.env.get_template(f"key_dataset_{version_tag}.jinja")
        rendered = (template.render(submission=model["submission"], program=model["program"], project=model["project"], resource=model["resource"],
                                    key_dataset=model["key_dataset"])
                     .replace('"none"', 'null').replace('"None"', 'null')
                     .replace('""','null'))
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_population_cedar_instance(self, model, version_tag):
        """
        Create the json that is a new resource to add to CEDAR for population data
        Parameters
        ----------
        model - the dictionary as found in PcorProcessResult that feeds the template

        Returns
        -------
        string with the resource json
        """
        logger.info("produce_population_cedar_instance()")
        template = self.env.get_template(f"population_data_resource_{version_tag}.jinja")
        rendered = (template.render(submission=model["submission"], program=model["program"], project=model["project"], resource=model["resource"],
                                    population_data_resource=model["population_data_resource"])
                     .replace('"none"', 'null').replace('"None"', 'null')
                     .replace('""','null'))
        logger.info("rendered: %s" % rendered)
        return rendered

    def produce_geo_tool_cedar_instance(self, model, version_tag):
        """
              Create the json that is a new resource to add to CEDAR for geo tool
              Parameters
              ----------
              model - the dictionary as found in PcorProcessResult that feeds the template

              Returns
              -------
              string with the resource json
              """
        logger.info("produce_geo_tool_cedar_instance()")
        template = self.env.get_template(f"cedar_geoexposure_tool_resource_{version_tag}.jinja")
        rendered = (template.render(submission=model["submission"], program=model["program"], project=model["project"],
                                    resource=model["resource"],
                                    geospatial_tool_resource=model["geospatial_tool_resource"])
                    .replace('"none"', 'null').replace('"None"', 'null')
                    .replace('""', 'null'))
        logger.info("rendered: %s" % rendered)
        return rendered
