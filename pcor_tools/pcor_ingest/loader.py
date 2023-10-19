import logging
from pcor_ingest.loader_cedar import LoaderCedar
from pcor_ingest.loader_spreadsheet import LoaderSpreadsheet

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class Loader:
    """
    Represents the main PCOR metadata loader
    """
    def __init__(self,pcor_ingest_configuration=None, loaders=None):
        """
        Main initialization method for PCOR loader
        """
        if loaders is None:
            loaders = {}
        self.loaders = loaders
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.loaders['spreadsheet'] = LoaderSpreadsheet(pcor_ingest_configuration=self.pcor_ingest_configuration)
        self.loaders['cedar'] = LoaderCedar()

    def process_pcor_load(self, loader_type=None, work_dir=None):
        logger.info('process_pcor_load()')
        logger.info('Loader type: %s ' % loader_type)
        logger.info('Work dir: %s ' % work_dir)
        if loader_type is not None:
            loader_type = self.loaders[loader_type]
            loader_type.process_load(self.pcor_ingest_configuration, work_dir=work_dir)
        else:
            logger.info('No loader found!')
            logger.info('loader_type is a required argument. Type can be ("spreadsheet" or "cedar")')
