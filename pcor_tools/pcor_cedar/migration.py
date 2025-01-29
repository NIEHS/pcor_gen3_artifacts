import json
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_parser_factory import CedarParserFactory
from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.loader_cedar import LoaderCedar

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarMigrate():

    def __init__(self, source_version=None, target_version=None):
        self.cedar_config = CedarConfig()
        self.cedar_access = CedarAccess()

        if not source_version:
            raise Exception("Source version is required")

        if not target_version:
            raise Exception("Target version is required")

        self.source_version = source_version
        self.target_version = target_version
        self.cedar_template_processor = CedarTemplateProcessor()

    def read_migrate_target(self, url):
        id = LoaderCedar.extract_id_for_resource(url)
        resource_json = self.cedar_access.retrieve_resource(id)
        tempfilename = f"{self.cedar_config.cedar_properties['working_directory']}/{id}.json"
        with open(tempfilename, "w") as f:
            json.dump(resource_json,f)

        reader_factory = CedarParserFactory()
        reader = reader_factory.instance(self.source_version)
        result = PcorProcessResult()
        reader.parse(tempfilename, result)
        if not result.success:
            logger.exception("parsing unsuccessful, error:%s" % result.message)
            raise Exception("parse error")

        return result.model_data

    def reformat_json(self, model_data):
        """
        Take the model data and create a json document of the right format

        Parameters
        ----------
        model_data : dict with the model data

        Returns
        -------
        json string with the new resource
        """
        logger.info('reformat_json()')
        if model_data["key_data"]:
            logger.info("migrating a geospatial_data_resource")
        else:
            raise Exception("not geospatial_data_resource, resource not supported")

        json_string = self.cedar_template_processor.produce_geospatial_cedar_instance(model_data, self.target_version)

        return json_string

    def store_migrated(self, migrated_json):
        logger.info("store_migrated")
        migration_folder = self.cedar_config.cedar_properties["migration.folder"]
        r_json = self.cedar_access.create_resource(migrated_json, migration_folder)
        return r_json["@id"]

    def migrate(self, resource_url):
        """
        migrate the source at the given location to the new target format
        Parameters
        ----------
        resource_url url where the resource to migrate can be found
        cedar_target_url

        Returns
        -------
        string with the name of the migrated resource
        """
        logger.info('migrate :: %s ' % (resource_url))

        if not resource_url:
            logger.exception("No resource url specified")
            raise Exception("no resource_url specified for migration")

        model = self.read_migrate_target(resource_url)
        # TODO: add annotation to submission comment?
        migrated_json = self.reformat_json(model)

        id = LoaderCedar.extract_id_for_resource(self.store_migrated(migrated_json))
        model_json = json.loads(migrated_json)
        name = model_json["RESOURCE"]["resource_name"]["@value"]
        self.cedar_access.rename_resource(id, name)
        return name


