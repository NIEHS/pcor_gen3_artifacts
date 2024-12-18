import logging
import math
import re
import sys
import traceback
import uuid
import json
import warnings
import pandas as pd
from datetime import datetime

from pcor_ingest.cedar_resource_reader import CedarResourceParser
from pcor_ingest.measures_rollup import PcorMeasuresRollup
from pcor_ingest.pcor_gen3_ingest import PcorGen3Ingest
from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel, \
    PcorIntermediateResourceModel, PcorIntermediateProgramModel, \
    PcorSubmissionInfoModel, PcorKeyDatasetModel
from pcor_ingest.pcor_template_parser import PcorTemplateParser
from pcor_ingest.pcor_template_process_result import PcorProcessResult

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class KeyDatasetResourceParser():
    """
    A parent class for a parser of a PCOR spreadsheet template for a key dataset
    """

    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest = PcorGen3Ingest(pcor_ingest_configuration)
        self.pcor_measures_rollup = PcorMeasuresRollup(pcor_ingest_configuration)
        self.yyyy_pattern = r"\b(\d{4})\b"
        self.pcor_ingest_configuration = pcor_ingest_configuration

    @staticmethod
    def make_complex_array_from_pubs(value):
        clean_value = PcorTemplateParser.sanitize_column(value, False)
        temp_list = []
        if clean_value:
            temp_list = [line.strip() for line in str(clean_value).split(';')]

        return temp_list

    def parse(self, template_absolute_path, results):
        """
               Parse a spreadsheet template for a file at a given absolute path
               :param template_absolute_path: absolute path to the template file
               :param result: PcorTemplateParseResult with the outcome
               """
        # example path /deep/documents/foo.xls
        logger.info("parse()")

        # NB does not call super() parse because the template is different and contains multiple key datasets in one
        # spreadsheet

        warnings.simplefilter(action='ignore', category=UserWarning)
        df = pd.read_excel(template_absolute_path, sheet_name=1, engine='openpyxl')

        ss_rows = df.shape[0]
        logging.debug("iterate looking for the start of the data")

        # right now assume data starts on row 2 (zero based)
        if ss_rows < 3:
            logger.info("no data to process")
            sys.exit(0)

        for i in range(2, ss_rows):

            result = PcorProcessResult()
            submission = PcorSubmissionInfoModel()
            submission.curator_email = self.pcor_ingest_configuration.submitter_email
            submission.template_source = template_absolute_path
            result.model_data["submission"] = submission

            if not submission.curator_email:
                logging.error("no curator email in pcor ingest configuration")
                raise Exception("no curator email in pcor ingest configuration")

            # Program

            program = PcorIntermediateProgramModel()
            program.name = PcorTemplateParser.sanitize_column(df.iat[i, 0])
            program.dbgap_accession_number = program.name
            result.model_data["program"] = program

            # Project

            project = PcorIntermediateProjectModel()
            project.code = PcorTemplateParser.sanitize_column(df.iat[i, 1])
            project.short_name = PcorTemplateParser.sanitize_column(df.iat[i, 2])
            project.name = PcorTemplateParser.sanitize_column(df.iat[i, 3])
            project.project_sponsor = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(df.iat[i, 4]))
            project.project_sponsor_type = PcorTemplateParser.make_array(
                PcorTemplateParser.sanitize_column(df.iat[i, 6]))

            #result.project_guid = project.submitter_id
            result.project_code = project.code
            PcorTemplateParser.process_project_identifiers(project)
            result.model_data["project"] = project

            # Resource and Key Dataset

            resource = PcorIntermediateResourceModel()
            resource.resource_type = "Data Resource"
            key_data_resource = PcorKeyDatasetModel()
            key_data_resource.display_type = "KeyDataset"

            # dataset name K (10)
            resource.name = PcorTemplateParser.sanitize_column(df.iat[i, 10])
            resource.short_name = resource.name
            resource.long_name = resource.name

            # domain L (11)

            resource.domain = PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 11])

            # resource summary H (7)

            resource.description = PcorTemplateParser.sanitize_column(df.iat[i, 7])

            # keywords N (13)

            resource.keywords = PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 13])

            # measures P (15)

            measures = PcorTemplateParser.make_complex_array(df.iat[i, 15])
            measures_rollup = self.pcor_measures_rollup.process_measures(measures)
            key_data_resource.measures = measures_rollup.measures
            key_data_resource.measures_parent = measures_rollup.measures_parents
            key_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            key_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor

            # format Q (16)

            key_data_resource.data_formats = PcorTemplateParser.make_array(
                PcorTemplateParser.sanitize_column(df.iat[i, 16]))

            # data access url (17)
            key_data_resource.data_location = PcorTemplateParser.make_complex_array(df.iat[i, 17])

            # publications (18) [try delimit by ;]

            resource.publications = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 18])

            # publication links (19)

            resource.publication_links = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 19])

            # spatial extent (20)
            key_data_resource.spatial_coverage = PcorTemplateParser.sanitize_column(df.iat[i, 20])

            # geometry type (21)

            key_data_resource.geometry_type = \
                PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(df.iat[i, 21]))

            # spatial resolution X (23)
            key_data_resource.spatial_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 23])

            # temporal extent begin AB (27)
            key_data_resource.time_extent_start_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 27])

            # temporal extent end AC (28)
            key_data_resource.time_extent_end_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 28])

            # temporal resolution AE (30)
            key_data_resource.temporal_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 30])

            # suggested uses AH (33) -> move this to comments - mc
            key_data_resource.comments = PcorTemplateParser.sanitize_column(df.iat[i, 33])

            # example individual level metrics AI (34)
            key_data_resource.metrics_derived_from_data_set = PcorTemplateParser.sanitize_column(df.iat[i, 34])

            # strengths AJ (35)
            resource.strengths = PcorTemplateParser.sanitize_column(df.iat[i, 35])

            # limitations AK (36)
            resource.limitations = PcorTemplateParser.sanitize_column(df.iat[i, 36])

            # example apps AF (3L)
            resource.example_applications = PcorTemplateParser.sanitize_column(df.iat[i, 37])

            # tools supporting use AM (32)
            resource.tools_supporting_uses = PcorTemplateParser.sanitize_column(df.iat[i, 38])

            if resource.submitter_id is None or resource.submitter_id == '':
                resource.submitter_id = str(uuid.uuid4())

            result.resource_guid = resource.submitter_id
            result.resource_name = resource.name

            result.model_data["resource"] = resource
            result.model_data["key_dataset"] = key_data_resource

            results.append(result)

