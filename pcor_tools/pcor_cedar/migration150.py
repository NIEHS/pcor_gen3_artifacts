import json
import logging
import os
import sys
from optparse import OptionParser

from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_ingest.pcor_template_process_result import PcorProcessResult

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_resource_reader_pre_150 import CedarResourceParserPre150

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.loader_cedar import LoaderCedar

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarMigrate150():
    def __init__(self, cedar_config_file):
        self.cedar_config = CedarConfig(cedar_config_file)
        self.cedar_access = CedarAccess()
        self.cedar_template_processor = CedarTemplateProcessor()

    def read_migrate_target(self, url):
        id = LoaderCedar.extract_id_for_resource(url)
        resource_json = self.cedar_access.retrieve_resource(id)
        tempfilename = f"{self.cedar_config.cedar_properties['working_directory']}/{id}.json"
        with open(tempfilename, "w") as f:
            json.dump(resource_json,f)

        reader = CedarResourceParserPre150()
        result = PcorProcessResult()
        reader.parse(tempfilename, result)
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
        if model_data["geospatial_data_resource"]:
            logger.info("migrating a geospatial_data_resource")
        else:
            raise Exception("not geospatial_data_resource, resource not supported")

        json_string = self.cedar_template_processor.produce_geospatial_cedar_instance(model_data, "151")

        return json_string

    def store_migrated(self, migrated_json):
        logger.info("store_migrated")
        migration_folder = self.cedar_config.cedar_properties["migration.folder"]
        self.cedar_access.create_resource(migrated_json, migration_folder)

    def migrate(self, resource_url):
        """
        migrate the source at the given location to the new target format
        Parameters
        ----------
        resource_url url where the resource to migrate can be found
        cedar_target_url

        Returns
        -------

        """
        logger.info('migrate :: %s ' % (resource_url))
        model = self.read_migrate_target(resource_url)
        # TODO: add annotation to submission comment?
        migrated_json = self.reformat_json(model)
        self.store_migrated(migrated_json)
        # add to local?


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-r', "--resource_url", action='store', dest='resource_url', default=None)
    #parser.add_option('-f', "--working_file", action='store', dest='working_file', default=None)
    parser.add_option('-t', "--cedar_target_url", action='store', dest='cedar_target_url', default=None)

    return parser.parse_args()[0]

def main():
    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    resource_url = args.resource_url # the resource to migrate, copied from the browser
    #working_file = args.working_file # scratch local working directory
    cedar_target_url = args.cedar_target_url # location for migrated file

    logger.info('resource to load :: %s' % resource_url)
    logger.info('cedar target :: %s' % cedar_target_url)

    migrator = CedarMigrate150()

    return migrator.migrate(resource_url, cedar_target_url)

if __name__ == "__main__":
    main()
