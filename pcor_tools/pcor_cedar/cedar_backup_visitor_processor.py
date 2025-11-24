import json
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_config import CedarConfig
from pcor_cedar.cedar_parser_factory import CedarParserFactory
from pcor_cedar.cedar_resource_reader_1_5_1 import CedarResourceReader_1_5_1
from pcor_ingest.loader import Loader
from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

class CedarBackupVisitor():
    """
    Abstract parent class for a visitor process to be invoked at each CEDAR document
    """

    def __init__(self):
        pass

    def visit(self, cedar_model: dict, file_name: str, pcor_measures_rollup:PcorMeasuresRollup):
        """
        notifies this visitor via callback that there is a cedar document to be processed
        :param pcor_measures_rollup: PcorMeasuresRollup object
        :param cedar_model: a dict with the CEDAR document contents
        :param file_name: the absolute path to the file that contains the CEDAR document contents
        :return: None (all processing is within the visitor)
        """
        pass

class CedarBackupVisitorProcessor():

    """
    Helper framework will crawl the cedar backup folder and invoke a visitor process at each CEDAR document
    """

    def __init__(self, visitor:CedarBackupVisitor, start_path:str = None):
        """
        A class responsible for managing the initialization process of a CedarBackupVisitor.
        :param visitor: The CedarBackupVisitor instance that is subclassed for purpose
        :type visitor: CedarBackupVisitor
        :param start_path: The absolute path to the folder that contains the CEDAR backup files. The root
        of the crawl
        :type start_path: str
        """
        self.visitor = visitor
        self.start_path = start_path
        self.cedar_resource_reader = CedarResourceReader_1_5_1()

    def start(self):
        """
        Starts the process of walking through the directory structure and visits each JSON file
        encountered using the CedarBackupVisitor.
        
        :return: None
        """

        if not self.start_path:
            raise ValueError("start_path must be specified")

        logger.info(f"Starting backup visitor processor with start path: {self.start_path}")

        for root, dirs, files in os.walk(self.start_path):
            # Process all JSON files in the current directory
            for file in files:
                if file.lower().endswith('.json'):
                    if 'templates' in root:
                        continue

                    if 'Old_Versions' in root:
                        continue

                    if 'Template' in file:
                        continue

                    json_path = os.path.join(root, file)
                    result = PcorProcessResult()
                    logger.info(f"parsing: {json_path}")
                    self.cedar_resource_reader.parse(json_path, result)
                    if result.success:

                        try:
                            self.visitor.visit(result.model_data,json_path, self.cedar_resource_reader.pcor_measures_rollup)
                        except Exception as e:
                            # Log error but continue processing other files
                            logger.error(f"Error processing {json_path}: {str(e)}")
                    else:
                        logger.error(f"Error processing {json_path}: {result.errors}")