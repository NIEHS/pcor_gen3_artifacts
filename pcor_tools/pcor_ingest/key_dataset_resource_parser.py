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
            #result.project_guid = project.submitter_id
            result.project_code = project.code
            if project.submitter_id == "" or project.submitter_id is None:
                project.submitter_id = str(uuid.uuid4())
            if project.code == "" or project.code is None:
                project.code = str(uuid.uuid4())
            if project.dbgap_accession_number == "" or project.dbgap_accession_number is None:
                project.dbgap_accession_number = project.submitter_id
            result.model_data["project"] = project

            # Resource and Key Dataset

            resource = PcorIntermediateResourceModel()
            resource.resource_type = "Data Resource"
            key_data_resource = PcorKeyDatasetModel()
            key_data_resource.display_type = "KeyDataset"

            # dataset name (6)
            resource.name = PcorTemplateParser.sanitize_column(df.iat[i, 6])
            resource.short_name = resource.name
            resource.long_name = resource.name

            # domain (7)

            resource.domain = PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 7])

            # resource summary (8)

            resource.description = PcorTemplateParser.sanitize_column(df.iat[i, 8])

            # keywords (12)

            resource.keywords = PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 12])

            # measures (10)

            measures = PcorTemplateParser.make_complex_array(df.iat[i, 10])
            measures_rollup = self.pcor_measures_rollup.process_measures(measures)
            key_data_resource.measures = measures_rollup.measures
            key_data_resource.measures_parent = measures_rollup.measures_parents
            key_data_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
            key_data_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor

            # format (11)

            key_data_resource.data_formats = PcorTemplateParser.make_array(
                PcorTemplateParser.sanitize_column(df.iat[i, 11]))

            # data access url (12)
            key_data_resource.data_location = PcorTemplateParser.make_complex_array(df.iat[i, 12])

            # publications (13) [try delimit by ;]

            resource.publications = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 13])

            # publication links (18) FIXME: now these are missing - mc

            #resource.publication_links = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 18])

            # spatial extent (14)
            key_data_resource.spatial_coverage = PcorTemplateParser.sanitize_column(df.iat[i, 14])

            # geometry type (15)

            key_data_resource.geometry_type = \
                PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(df.iat[i, 15]))

            # spatial resolution R (17)
            key_data_resource.spatial_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 17])

            # temporal extent begin V (21)
            key_data_resource.time_extent_start_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 21])

            # temporal extent end W (22)
            key_data_resource.time_extent_end_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 22])

            # temporal resolution Y (24)
            key_data_resource.temporal_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 24])

            # suggested uses AB (27) -> move this to comments - mc
            key_data_resource.comments = PcorTemplateParser.sanitize_column(df.iat[i, 27])

            # example individual level metrics AC (28)
            key_data_resource.metrics_derived_from_data_set = PcorTemplateParser.sanitize_column(df.iat[i, 28])

            # strengths AD (29)
            resource.strengths = PcorTemplateParser.sanitize_column(df.iat[i, 29])

            # limitations AE (30)
            resource.limitations = PcorTemplateParser.sanitize_column(df.iat[i, 30])

            # example apps AF (31)
            resource.example_applications = PcorTemplateParser.sanitize_column(df.iat[i, 31])

            # tools supporting use AG (32)
            resource.tools_supporting_uses = PcorTemplateParser.sanitize_column(df.iat[i, 32])

            if resource.submitter_id is None or resource.submitter_id == '':
                resource.submitter_id = str(uuid.uuid4())

            result.resource_guid = resource.submitter_id
            result.resource_name = resource.name

            result.model_data["resource"] = resource
            result.model_data["key_dataset"] = key_data_resource

            results.append(result)

