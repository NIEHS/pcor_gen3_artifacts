import logging

from pcor_cedar.cedar_config import CedarConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class CedarAccess(object):

    def __init__(self, cedar_file_name):
        self.cedar_file_name = cedar_file_name
        if cedar_file_name:
            self.cedar_config = CedarConfig(cedar_file_name)
        else:
            raise "no config file found"


    def retrieve_chords_folder_contents(self):
        pass