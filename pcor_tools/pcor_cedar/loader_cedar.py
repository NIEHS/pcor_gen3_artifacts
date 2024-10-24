import json
import logging
import os
import re
import shutil
import sys
from optparse import OptionParser

from pcor_ingest.pcor_reporter import PcorReporter

from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

from pcor_cedar.cedar_resource_reader import CedarResourceParser
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError

from pcor_cedar.cedar_access import CedarAccess
from pcor_ingest.loader import Loader

from pcor_cedar.cedar_config import CedarConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class LoaderCedar(Loader):
    def __init__(self, pcor_ingest_configuration):
        super().__init__(pcor_ingest_configuration)
        self.cedar_config = CedarConfig()
        self.cedar_access = CedarAccess()
        self.reader = CedarResourceParser(pcor_ingest_configuration=self.pcor_ingest_configuration)
        self.pcor_reporter = PcorReporter(pcor_ingest_configuration)

        self.validate_sub_folders(pcor_ingest_configuration.working_directory)
        #cedar_folder = pcor_ingest_configuration.working_folder + "/cedar"
        #os.mkdir(cedar_folder)
        #self.cedar_folder = cedar_folder

    def process_load(self, file_path=None):
        logger.info('file_path dir: %s ' % file_path)
        work_dir = os.path.abspath(file_path)
        logger.info('work_dir dir: %s ' % work_dir)
        self.validate_sub_folders(work_dir=work_dir)
        logger.info('Getting listing of cedar resources')
        loader_collection = self.cedar_access.retrieve_loading_contents()
        for resource in loader_collection.subfolders:
            logger.info("resource: %s" % resource)
            if resource.item_type != 'instance':
                logger.debug('skipping item, not an instance')
                continue
            logger.info("have an instance")
            instance_json = self.cedar_access.retrieve_resource(LoaderCedar.extract_id_for_resource(resource.folder_id))
            logger.debug("instance json: %s" % instance_json)
            self.load_resource(instance_json)

    def process_individual_load(self,resource_url=None):
        logger.info('process_individual_load')
        logger.info('resource_url: %s' % resource_url)

        # write the json to a file in processing and then proceed
        guid = LoaderCedar.extract_id_for_resource(resource_url)
        instance_json = self.cedar_access.retrieve_resource(guid)

        result = self.load_resource(instance_json)
        return result


    def load_resource(self, resource):

        """
        Load the resource in the given cedar json
        Parameters
        ----------
        resource JSON form CEDAR

        Returns
        -------

        PcorProcessResult

        """
        logger.info("load resource: %s" % resource)
        result = PcorProcessResult()
        #result.template_source = resource.folder_id
        result.endpoint = self.pcor_ingest_configuration.gen3_endpoint

        try:

            # bring the resource down to cedar_staging, use the guid as the file name
            guid =  LoaderCedar.extract_id_for_resource(resource["@id"])
            logger.debug("writing file for: %s" % guid)
            processing_file_path = self.pcor_ingest_configuration.working_directory + '/processing/' + guid + '.json'
            with open(processing_file_path, 'w') as f:
                json.dump(resource, f)

            logger.debug("file written: %s" % f.name)

            # marshal the json data into the intermediate data model

            self.reader.parse(f.name, result)

            if not result.success:
                logger.warning("unsuccessful parsing, do not process")
            else:
                process_template = PcorTemplateProcessor(pcor_ingest_configuration=self.pcor_ingest_configuration)
                process_template.process(result)

        except Exception as e:
            logger.error('Error occurred: %s' % str(e))
            result.success = False
            pcor_error = PcorError()
            pcor_error.type = ""
            pcor_error.key = ""
            pcor_error.message = str(e)
            result.errors.append(pcor_error)

        if result.success:
            # processed folder
            # result.success --> true
            # result --> move file to processed folder
            success_path = os.path.join(self.workspace_processed_folder_path,
                                        os.path.basename(processing_file_path))
            result.template_current_location = success_path

            shutil.move(src=processing_file_path, dst=success_path)
        else:
            # failed folder
            # result.success --> false
            # result --> move file to failed folder
            failed_path = os.path.join(self.workspace_failed_folder_path,
                                       os.path.basename(processing_file_path))

            shutil.move(src=processing_file_path, dst=self.workspace_failed_folder_path)
            result.template_current_location = failed_path

        self.pcor_reporter.report(result)

        return result

    @staticmethod
    def extract_id_for_resource(resource_url):
        # Regex pattern to match a GUID
        guid_pattern = r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'

        # Find all GUIDs in the URL
        match = re.findall(guid_pattern, resource_url)

        # Check if a match was found and output the result
        if match:
            extracted_guid = match[0]  # Get the first GUID
            return extracted_guid
        else:
            raise ValueError("No GUID in provided URL")


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-r', "--resource_url", action='store', dest='resource_url', default=None)
    parser.add_option('-f', "--working_file", action='store', dest='working_file', default=None)

    return parser.parse_args()[0]

def main():
    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "CEDAR_PROPERTIES" not in os.environ:
        logger.error("CEDAR_PROPERTIES not found in env. System exiting...")
        sys.exit()

    if "PCOR_GEN3_CONFIG_LOCATION" not in os.environ:
        logger.error("PCOR_GEN3_CONFIG_LOCATION not found in env. System exiting...")
        sys.exit()

    resource_url = args.resource_url
    working_file = args.working_file

    if not os.path.exists(working_file):
        logger.error('ERROR: working_file does not exist. System will exit now...')
        sys.exit()
    else:
        logger.info('working_file: %s' % working_file)

    logger.info('resource to load :: %s' % resource_url)
    pcor_ingest_configuration = PcorIngestConfiguration.load_pcor_ingest_configuration_from_env()
    loader_cedar = LoaderCedar(pcor_ingest_configuration=pcor_ingest_configuration)

    if resource_url is None:
        return loader_cedar.process_load(working_file)
    else:
        return loader_cedar.process_individual_load(resource_url)



if __name__ == "__main__":
    main()
