import logging
import sys
import uuid
import warnings

import pandas as pd
import validators

from pcor_ingest.measures_rollup import PcorMeasuresRollup
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
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.pcor_measures_rollup = PcorMeasuresRollup(pcor_ingest_configuration.measures_rollup)
        self.yyyy_pattern = r"\b(\d{4})\b"

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
        df = pd.read_excel(template_absolute_path, sheet_name=2, engine='openpyxl')

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

            #if not submission.curator_email:
            #    logging.error("no curator email in pcor ingest configuration")
            #    raise Exception("no curator email in pcor ingest configuration")

            # Program

            program = PcorIntermediateProgramModel()
            program.name = PcorTemplateParser.sanitize_column(df.iat[i, 0])
            if not program.name:
                logger.info("skipping blank row due to missing program name")
                continue

            program.dbgap_accession_number = program.name
            result.model_data["program"] = program

            # Project

            project = PcorIntermediateProjectModel()
            project.code = PcorTemplateParser.sanitize_column(df.iat[i, 1])
            project.short_name = PcorTemplateParser.sanitize_column(df.iat[i, 2])
            project.name = PcorTemplateParser.sanitize_column(df.iat[i, 3])
            project.project_sponsor = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(df.iat[i, 4]))

            temp_proj_sponsor_other = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(df.iat[i, 5]))

            for entry in temp_proj_sponsor_other:
                if entry not in project.project_sponsor:
                    project.project_sponsor_other.pop(entry)

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

            # key variables (14)
            resource.use_key_variables = PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 14])

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
            key_data_resource.data_link = PcorTemplateParser.make_complex_array(df.iat[i, 17])

            # publications (18) [try delimit by ;]

            resource.publications = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 18])

            # publication links (19)
            resource.publication_links = KeyDatasetResourceParser.make_complex_array_from_pubs(df.iat[i, 19])

            # spatial coverage (20)
            key_data_resource.spatial_coverage =  PcorTemplateParser.make_array(
                PcorTemplateParser.sanitize_column(df.iat[i, 20]))

            # geometry type (21)
            key_data_resource.geometry_type = \
                PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(df.iat[i, 21]))

            key_data_resource.spatial_resolution_all_available = (
                PcorTemplateParser.make_complex_camel_case_array(df.iat[i, 22]))

            # spatial resolution X (23)
            key_data_resource.spatial_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 23])

            # spatial resolution other (24)
            val = PcorTemplateParser.sanitize_column(df.iat[i, 24])
            if val:
                key_data_resource.spatial_resolution_other.append(val)

            # temporal extent begin AB (27)
            key_data_resource.time_extent_start_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 27])

            # temporal extent end AC (28)
            key_data_resource.time_extent_end_yyyy = PcorTemplateParser.format_date_time(df.iat[i, 28])

            # temporal resolution AE (30)
            key_data_resource.temporal_resolution = PcorTemplateParser.sanitize_column(df.iat[i, 30])

            # suggested uses AH (33) -> move this to comments - mc
            key_data_resource.comments = PcorTemplateParser.sanitize_column(df.iat[i, 33])

            key_data_resource.use_suggested = PcorTemplateParser.new_make_array_with_delim(df.iat[i, 33],';', False)

            # example metric AI (34) txlate to array entry
            metric = PcorTemplateParser.sanitize_column(df.iat[i, 34])

            if metric:
                key_data_resource.use_example_metrics = PcorTemplateParser.make_array_split_semicolon(metric)

            # example individual level metrics AI (34)
            key_data_resource.metrics_derived_from_data_set = PcorTemplateParser.sanitize_column(df.iat[i, 34])

            # strengths AJ (35)
            resource.strengths = PcorTemplateParser.make_array_split_semicolon(df.iat[i, 35])
            key_data_resource.use_strengths = resource.strengths

            # limitations AK (36)
            resource.limitations = PcorTemplateParser.make_array_split_semicolon(df.iat[i, 36])
            key_data_resource.use_limitations = resource.limitations

            # example apps AF (37)
            resource.example_applications = PcorTemplateParser.sanitize_column(df.iat[i, 37])

            if validators.url(resource.example_applications):
                key_data_resource.use_example_application_text.append("")
                key_data_resource.use_example_application_link.append(resource.example_applications)
            else:
                key_data_resource.use_example_application_text.append(resource.example_applications)
                key_data_resource.use_example_application_link.append("http://nolink")

            # tools supporting use AM (32)
            resource.tools_supporting_uses = PcorTemplateParser.sanitize_column(df.iat[i, 38])

            if validators.url(resource.tools_supporting_uses):
                key_data_resource.use_tools_text.append("")
                key_data_resource.use_tool_link.append(resource.tools_supporting_uses)
            else:
                key_data_resource.use_tools_text.append(resource.tools_supporting_uses)
                key_data_resource.use_tool_link.append("http://nolink")

            # key variables O (14)
            key_data_resource.use_key_variables = PcorTemplateParser.make_array(
                PcorTemplateParser.sanitize_column(df.iat[i, 14]))

            if resource.submitter_id is None or resource.submitter_id == '':
                resource.submitter_id = str(uuid.uuid4())

            result.resource_guid = resource.submitter_id
            result.resource_name = resource.name

            result.model_data["resource"] = resource
            result.model_data["key_dataset"] = key_data_resource

            results.append(result)

