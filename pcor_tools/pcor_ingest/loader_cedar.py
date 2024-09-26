import logging
import os

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





