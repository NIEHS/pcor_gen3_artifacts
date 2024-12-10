import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from optparse import OptionParser

from pcor_cedar.cedar_loader_preprocessor import CedarLoaderPreprocessor
from pcor_cedar.cedar_parser_factory import CedarParserFactory
from pcor_ingest.pcor_reporter import PcorReporter

from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
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
    def __init__(self, pcor_ingest_configuration, cedar_version):
        super().__init__(pcor_ingest_configuration)
        self.cedar_config = CedarConfig()
        self.cedar_access = CedarAccess()
        self.cedar_version = cedar_version
        reader_factory = CedarParserFactory()
        self.reader = reader_factory.instance(cedar_version)
        self.pcor_reporter = PcorReporter(pcor_ingest_configuration)

        self.validate_sub_folders(pcor_ingest_configuration.working_directory)
        #cedar_folder = pcor_ingest_configuration.working_folder + "/cedar"
        #os.mkdir(cedar_folder)
        #self.cedar_folder = cedar_folder

    def process_load_from_cedar_directory(self, directory=None):
        work_dir = self.pcor_ingest_configuration.working_directory
        logger.info('work_dir dir: %s ' % work_dir)
        self.validate_sub_folders(work_dir=work_dir)
        logger.info('Getting listing of cedar resources')
        loader_collection = self.cedar_access.retrieve_loading_contents(directory)
        for resource in loader_collection.subfolders:
            logger.info("resource: %s" % resource)
            if resource.item_type != 'instance':
                logger.debug('skipping item, not an instance')
                continue
            logger.info("have an instance")
            instance_json = self.cedar_access.retrieve_resource(LoaderCedar.extract_id_for_resource(resource.folder_id))
            logger.debug("instance json: %s" % instance_json)
            self.load_resource(instance_json)

    def process_individual_load_of_cedar_resource_from_url(self, resource_url=None):
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
        guid = LoaderCedar.extract_id_for_resource(resource["@id"])

        processing_file_path = LoaderCedar.add_timestamp_to_file(
            self.pcor_ingest_configuration.working_directory + '/processing/' + guid + '.json')

        try:

            # bring the resource down to cedar_staging, use the guid as the file name
            logger.debug("writing file for: %s" % guid)
            with open(processing_file_path, 'w') as f:
                json.dump(resource, f)

            logger.debug("file written: %s" % f.name)

            # marshal the json data into the intermediate data model

            self.reader.parse(f.name, result)

            # collapse other fields
            preprocessor = CedarLoaderPreprocessor()
            preprocessor.process(result.model_data)

            if not result.success:
                logger.warning("unsuccessful parsing, do not process")
            else:
                process_template = PcorTemplateProcessor(pcor_ingest_configuration=self.pcor_ingest_configuration) # FIXME: temp mute
                process_template.process(result)
                pass

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

    def main_load_process(self, resource_url=None, directory=None):

        file_path = self.pcor_ingest_configuration.working_directory

        if not os.path.exists(file_path):
            logger.error('ERROR: working_file does not exist. System will exit now...')
            sys.exit()
        else:
            logger.info('file_path: %s' % file_path)

        logger.info('resource to load :: %s' % resource_url)
        logger.info('directory: %s' % directory)

        if resource_url:
            return self.process_individual_load_of_cedar_resource_from_url(resource_url=resource_url)
        elif directory:
            return self.process_load_from_cedar_directory(directory=directory)
        else:
            logger.error("must add the -r or -d flag for a resc url or a folder url")
            raise Exception("must add the -r or -d flag for a resc url or a folder url")

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

    @staticmethod
    def add_timestamp_to_file(file_name):
        # test1~pcor~_23_06_29_124427.json
        try:
            idx = file_name.index('~pcor~')
            file_part = file_name[0:idx]
            new_file_name = file_part + '~pcor~' + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.json'
            return new_file_name
        except ValueError:
            new_file_name = file_name.replace('.json', '~pcor~'
                                              + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.json')
            logger.info("new file name:%s" % new_file_name)
            return new_file_name
