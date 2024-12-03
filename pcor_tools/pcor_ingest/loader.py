import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class Loader:
    """
    Represents the main PCOR metadata loader
    """

    def __init__(self, pcor_ingest_configuration=None):
        """
        Main initialization method for PCOR loader
        """
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.pcor_ingest_configuration = pcor_ingest_configuration

    def process_pcor_load(self, loader_type=None, file_path=None):
        logger.info('process_pcor_load()')
        logger.info('Loader type: %s ' % loader_type)
        logger.info('file_path dir: %s ' % file_path)
        if loader_type is not None:
            loader_type = self.loaders[loader_type]
            loader_type.process_load_from_cedar_directory(file_path=file_path)
        else:
            logger.info('No loader found!')
            logger.info('loader_type is a required argument. Type can be ("spreadsheet" or "cedar")')

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
