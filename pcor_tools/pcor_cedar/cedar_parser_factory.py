import logging

from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_resource_reader_1_5_0 import CedarResourceReader_1_5_0
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

"""
Factory class will initialize a CEDAR resource parser for a given version number

"""
class CedarParserFactory:

    def __init__(self):
        self.cedar_config = CedarConfig()

    def instance(self, source_version):
        """
        Create an instance of a CEDAR resource reader for a given version string (in X_X_X format, can include
        an _xxxx suffix for a special subvariant of a reader

        Parameters
        ----------
        source_version version of the reader in X_X_X format desired

        Returns
        -------

        subclass of CedarResourceReader appropriate to the given version

        """

        if source_version is None:
            raise Exception("No source version specified")

        if source_version == '1_5_0':
            return CedarResourceReader_1_5_0()
        elif source_version == '1_5_1':
            return CedarResourceReader_1_5_1()

        else:
            raise Exception("Unknown source version: {}".format(source_version))

