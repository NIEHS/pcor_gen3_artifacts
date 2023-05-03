import json
import os
import logging

from unittest import TestCase
import requests

from pcor_ingest.pcor_template_processor import PcorTemplateProcessor
from tests import pcor_testing_utilities

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, PcorIntermediateResourceModel, \
    PcorDiscoveryMetadata, Tag, AdvSearchFilter, PcorGeospatialDataResourceModel, PcorPopDataResourceModel, \
    PcorProgramModel, PcorGeoToolModel

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class TestPcorTemplateProcessor(TestCase):
    def test_process_add_program(self):
        logger.info('test_process_add_program')
        process_template = PcorTemplateProcessor()
        program = PcorProgramModel()
        program.name = 'NFS'
        program.dbgap_accession_number = 'NFS'
        model_data = {
            'program': program
        }
        process_template.process(template_absolute_path='test_location', model_data=model_data)
