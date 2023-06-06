import logging
import os
import shutil
import requests

from datetime import datetime, date
from pcor_ingest.ingest_context import PcorIngestConfiguration
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError
from pcor_ingest.spreadsheet_reader import PcorSpreadsheeetReader
from pcor_ingest.pcor_result_handler import PcorResultHandler

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
        self.result_handler = PcorResultHandler(pcor_ingest_configuration)

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

    def process_load(self, pcor_ingest_configuration=None, work_dir=None):
        """
        Load a spreadsheet template
        """
        logger.info('process_load()')
        logger.info('Work dir: %s ' % work_dir)
        self.validate_sub_folders(work_dir=work_dir)
        logger.info('Checking for new SS files')
        file_list = os.listdir(self.workspace_new_folder_path)
        if file_list:
            logger.info('Files found: %s' % str(file_list))
            for file in file_list:
                if file.endswith('.xlsm'):
                    logger.info('Spreadsheet found: %s' % file)

                    # new folder
                    file_path = os.path.join(self.workspace_new_folder_path, file)
                    logger.info(
                        '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                        file, file_path, self.workspace_processing_folder_path))
                    shutil.move(src=file_path, dst=self.workspace_processing_folder_path)

                    # processing folder
                    result = PcorProcessResult()
                    log_file_path = None
                    file_path = os.path.join(self.workspace_processing_folder_path, file)
                    ss_reader = PcorSpreadsheeetReader(pcor_ingest_configuration=self.pcor_ingest_configuration)

                    try:
                        result = ss_reader.process_template_instance(file_path)

                    except Exception as e:
                        logger.error('Error occurred: %s' % str(e))
                        log_file_name = file.split('.')[0] + '.log'
                        log_file_path = os.path.join(self.workspace_processing_folder_path, log_file_name)
                        file = open(log_file_path, "w")
                        file.write('Error occurred \n %s' % str(e))
                        file.close()
                        result.success = False
                        result.template_source = file_path
                        pcor_error = PcorError()
                        pcor_error.type = ""
                        pcor_error.key = ""
                        pcor_error.message=str(e)
                        result.errors.append(pcor_error)

                    result.template_source = file_path
                    self.result_handler.handle_result(result)

                    if result.success:
                        # processed folder
                        # result.success --> true
                        # result --> move file to processed folder

                        dest = os.path.join(self.workspace_processed_folder_path, os.path.basename(file_path))
                        dest_with_timestamp = dest.replace('.xlsm', str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm')
                        logger.info(
                            '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                                file, file_path, dest_with_timestamp))
                        shutil.move(src=file_path, dst=dest_with_timestamp)
                    else:
                        # failed folder
                        # result.success --> false
                        # result --> move file to failed folder
                        dest = os.path.join(self.workspace_failed_folder_path, os.path.basename(file_path))
                        dest_with_timestamp = dest.replace('.xlsm',
                                                           str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm')

                        logger.info(
                            '\nMoving file: %s \nsrc: %s\ndst: %s' % (
                                file, file_path, dest_with_timestamp))
                        shutil.move(src=file_path, dst=self.workspace_failed_folder_path)
                        if os.path.exists(log_file_path):
                            shutil.move(src=log_file_path, dst=dest_with_timestamp)

                else:
                    logger.info('Ignore non spreadsheet file: %s' % file)

        else:
            logger.info('No files found!')
