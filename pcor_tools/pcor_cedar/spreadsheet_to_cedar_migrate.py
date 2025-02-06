import json
import logging

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_cedar.loader_cedar import LoaderCedar
from pcor_ingest.pcor_template_process_result import PcorProcessResult
from pcor_ingest.spreadsheet_reader import PcorSpreadsheetReader

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


"""
Tool to migrate spreadsheets in version 1.4.1 into cedar 1.5.1

"""

class SpreadsheetCedarMigrate():

    def __init__(self, cedar_config, pcor_ingest_configuration):
        self.cedar_config = cedar_config
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.cedar_access = CedarAccess()
        self.cedar_template_processor = CedarTemplateProcessor()
        self.pcor_spreadsheet_reader = PcorSpreadsheetReader(pcor_ingest_configuration)

    def reformat_json(self, model_data, target_version):
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
        if model_data.get("geospatial_data_resource"):
            logger.info("migrating a geospatial_data_resource")
            json_string = self.cedar_template_processor.produce_geospatial_cedar_instance(model_data, target_version)
            return json_string
        elif model_data.get("population_data_resource"):
            logger.info("migrating a population_data_resource")
            json_string = self.cedar_template_processor.produce_population_cedar_instance(model_data, target_version)
            return json_string
        elif model_data.get("geospatial_tool_resource"):
            logger.info("migrating a geospatial_tool_resource")
            json_string = self.cedar_template_processor.produce_geo_tool_cedar_instance(model_data, target_version)
            return json_string
        elif model_data.get("key_dataset"):
            logger.info("migrating a key_dataset")
            json_string = self.cedar_template_processor.produce_key_dataset_cedar_instance(model_data, target_version)
            return json_string
        else:
            raise Exception("not geospatial_data_resource, resource not supported")



    def store_migrated(self, migrated_json):
        logger.info("store_migrated")
        migration_folder = self.cedar_config.cedar_properties["migration.folder"]
        r_json = self.cedar_access.create_resource(migrated_json, migration_folder)
        return r_json["@id"]


    def read_migrate_target(self, target_path):
        logger.info("read_migrate_target: %s", target_path)
        result = PcorProcessResult()
        result.endpoint = self.pcor_ingest_configuration.gen3_endpoint
        result.template_source = target_path
        self.pcor_spreadsheet_reader.process_template_instance(target_path,result)
        return result

    def migrate(self, source_file, target_version='1_5_1'):
        """
        migrate the individual source at the given location to the new target format
        Parameters
        ----------
       file path where the resource to migrate can be found
        source_file

       cedar template version that is the target target_version

        Returns the name of the migrated file
        -------
        string with the name of the migrated resource
        """

        logger.info('migrate :: %s ' % (source_file))

        if not source_file:
            logger.exception("No source_file specified")
            raise Exception("no source_file specified for migration")

        result = self.read_migrate_target(source_file)

        submission = result.model_data["submission"]
        if submission.curation_comment is None:
            submission.curation_comment = ""

        submission.curation_comment += "migrated from spreadsheet %s into CEDAR va pcor_tools" % source_file
        migrated_json = self.reformat_json(result.model_data, target_version=target_version)

        id = LoaderCedar.extract_id_for_resource(self.store_migrated(migrated_json))
        model_json = json.loads(migrated_json)
        name = model_json["RESOURCE"]["resource_name"]["@value"]
        self.cedar_access.rename_resource(id, name)
        return name


