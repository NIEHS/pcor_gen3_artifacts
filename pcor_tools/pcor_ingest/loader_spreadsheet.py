import logging
import os
import time
import shutil
from datetime import datetime

from pcor_ingest.spreadsheet_reader import PcorSpreadsheetReader

from pcor_ingest.pcor_template_processor import PcorTemplateProcessor
from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class LoaderSpreadsheet:
    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.workspace_folder_path = None
        self.workspace_new_folder_path = None
        self.workspace_processing_folder_path = None
        self.workspace_processed_folder_path = None
        self.workspace_failed_folder_path = None
        self.pcor_reporter = PcorReporter(pcor_ingest_configuration)

    def validate_sub_folders(self, work_dir=None):
        # new files folder
        self.workspace_folder_path = work_dir
        self.workspace_new_folder_path = os.path.join(self.workspace_folder_path, 'new')

        # when loader is processing the file
        self.workspace_processing_folder_path = os.path.join(self.workspace_folder_path, 'processing')
        if not os.path.exists(self.workspace_processing_folder_path):
            os.mkdir(self.workspace_processing_folder_path)

        # when loader is processing the file successfully
        self.workspace_processed_folder_path = os.path.join(self.workspace_folder_path, 'processed')
        if not os.path.exists(self.workspace_processed_folder_path):
            os.mkdir(self.workspace_processed_folder_path)

        # when loader is processing the file failed
        self.workspace_failed_folder_path = os.path.join(self.workspace_folder_path, 'failed')
        if not os.path.exists(self.workspace_failed_folder_path):
            os.mkdir(self.workspace_failed_folder_path)

    def process_load(self, file_path=None):
        """
        Load a spreadsheet template
        """
        logger.info('process_load()')
        logger.info('file_path dir: %s ' % file_path)
        work_dir = os.path.dirname(os.path.dirname(file_path))
        logger.info('work_dir dir: %s ' % work_dir)
        self.validate_sub_folders(work_dir=work_dir)

        file = os.path.basename(file_path)

        if file.endswith('.xlsm'):
            logger.info('Spreadsheet found: %s' % file)

            # new folder
            file_path = os.path.join(self.workspace_new_folder_path, file)
            new_file_name = LoaderSpreadsheet.add_timestamp_to_file(file)
            processing_file_path = self.workspace_processing_folder_path + '/' + new_file_name
            logger.info(
                '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                    file, file_path, self.workspace_processing_folder_path))
            shutil.move(src=file_path, dst=processing_file_path)

            # processing folder
            result = PcorProcessResult()
            result.template_source = file_path
            result.endpoint = self.pcor_ingest_configuration.gen3_endpoint
            ss_reader = PcorSpreadsheetReader(pcor_ingest_configuration=self.pcor_ingest_configuration)

            try:
                result = ss_reader.process_template_instance(processing_file_path,
                                                             result)  # took result out and made a param

                # FIXME: right here it picks the parser based on the ss type, but currently the parser is calling processor
                # do the processing stuff here for a template
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
        else:
            logger.info('Ignore non spreadsheet file: %s' % file)

    @staticmethod
    def add_timestamp_to_file(file_name):
        # test1~pcor~_23_06_29_124427.xlsm
        try:
            idx = file_name.index('~pcor~')
            file_part = file_name[0:idx]
            new_file_name = file_part + '~pcor~' + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm'
            return new_file_name
        except ValueError:
            new_file_name = file_name.replace('.xlsm', '~pcor~'
                                              + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm')
            logger.info("new file name:%s" % new_file_name)
            return new_file_name
