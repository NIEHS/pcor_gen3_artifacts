import logging
import os

from pcor_ingest.pcor_template_process_result import PcorProcessResult

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

    def process_load(self, file_path=None):
        logger.info('file_path dir: %s ' % file_path)
        work_dir = os.path.dirname(os.path.dirname(file_path))
        logger.info('work_dir dir: %s ' % work_dir)
        self.validate_sub_folders(work_dir=work_dir)
        file = os.path.basename(file_path)
        logger.info('Getting listing of cedar resources')
        loader_collection = self.cedar_access.retrive_loading_contents()
        for resource in loader_collection.subfolders:
            logger.info("resource: %s" % resource)
            if resource.item_type != 'instance':
                logger.debug('skipping item, not an instance')
                continue
            logger.info("have an instance")
            instance_json = self.cedar_access.retrieve_resource(resource.folder_id)
            logger.debug("instance json: %s" % instance_json)


    def load_resource(self, resource):
        logger.info("load resource: %s" % resource)
        result = PcorProcessResult()
        result.template_source = resource.folder_id
        result.endpoint = self.pcor_ingest_configuration.gen3_endpoint

        cedar_reader = PcorSpreadsheetReader(pcor_ingest_configuration=self.pcor_ingest_configuration)

        try:
            result = ss_reader.process_template_instance(processing_file_path,
                                                         result)  # took result out and made a param
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
            logger.info(
                '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                    new_file_name, processing_file_path, success_path))
            shutil.move(src=processing_file_path, dst=success_path)
        else:
            # failed folder
            # result.success --> false
            # result --> move file to failed folder
            failed_path = os.path.join(self.workspace_failed_folder_path,
                                       os.path.basename(processing_file_path))
            logger.info(
                '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                    new_file_name, processing_file_path, failed_path))
            shutil.move(src=processing_file_path, dst=self.workspace_failed_folder_path)
            result.template_current_location = failed_path
        self.pcor_reporter.report(result)


