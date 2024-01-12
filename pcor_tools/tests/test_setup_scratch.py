import os
import sys
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
logger = logging.getLogger(__name__)


def setup_scratch(path=None):
    """
    Setup pcor_work_dir at given path
    :param path: folder location

    ➜  pcor_work_dir tree
    .
    ├── failed
    ├── new
    ├── processed
    └── processing
    """
    logger.info('setup_scratch()')
    if path is not None:
        logger.info('path: %s', path)

        if not os.path.exists(path):
            logger.info('Scratch work dir does not exist, creating...')
            os.mkdir(path)
            os.makedirs(os.path.join(path, 'failed'), exist_ok=True)
            os.makedirs(os.path.join(path, 'new'), exist_ok=True)
            os.makedirs(os.path.join(path, 'processed'), exist_ok=True)
            os.makedirs(os.path.join(path, 'processing'), exist_ok=True)
        else:
            logger.info('Scratch work dir exists, creating subdirs...')
            os.makedirs(os.path.join(path, 'failed'), exist_ok=True)
            os.makedirs(os.path.join(path, 'new'), exist_ok=True)
            os.makedirs(os.path.join(path, 'processed'), exist_ok=True)
            os.makedirs(os.path.join(path, 'processing'), exist_ok=True)
    else:
        logger.error("path arg cannot be empty. System exiting...")
        sys.exit()


