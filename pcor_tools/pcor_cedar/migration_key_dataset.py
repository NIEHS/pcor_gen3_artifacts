import json
import logging
import os
import sys
import time
import shutil
from datetime import datetime

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_template_processor import CedarTemplateProcessor
from pcor_cedar.loader_cedar import LoaderCedar
from pcor_cedar.migration import CedarMigrate
from pcor_cedar.spreadsheet_to_cedar_migrate import SpreadsheetCedarMigrate
from pcor_ingest.key_dataset_resource_parser import KeyDatasetResourceParser
from pcor_ingest.pcor_intermediate_model import PcorSubmissionInfoModel
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor
from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

class CedarMigrateKeyDataset(SpreadsheetCedarMigrate):
    def __init__(self, cedar_config, pcor_ingest_configuration):
        super().__init__(cedar_config, pcor_ingest_configuration)
        self.pcor_ingest_configuration = pcor_ingest_configuration

    def migrate(self, source_file, target_version='1_5_1'):
        """
        migrate the individual source at the given location to the new target format. Key
        datasets have a one row per key dataset format
        Parameters
        ----------
       file path where the resource to migrate can be found
        source_file

       cedar template version that is the target target_version

        Returns the name of the migrated file
        -------
        string with the name of the migrated resource
        """
        logger.info('migrate :: %s ' % (source_file))

        if not source_file:
            logger.exception("No source_file specified")
            raise Exception("no source_file specified for migration")

        # processing folder
        results = []

        ss_reader = KeyDatasetResourceParser(self.pcor_ingest_configuration)

        any_error = False

        # parse is going to build an array of results, as the spreadheet contains multiple curated data sets

        try:
            ss_reader.parse(source_file, results)  # took result out and made a param
        except Exception as e:
            logger.error('Error occurred: %s' % str(e))
            any_error = True
            result = PcorProcessResult()
            submission = PcorSubmissionInfoModel()
            submission.curator_email = self.pcor_ingest_configuration.submitter_email
            submission.template_source = source_file
            result.model_data["submission"] = submission
            result.success = False
            pcor_error = PcorError()
            pcor_error.type = ""
            pcor_error.key = ""
            pcor_error.message = str(e)
            result.errors.append(pcor_error)

        if not any_error:

            logger.info("no parse error, continue with processing")

            for result in results:

                if not result.success: # skip things that didn't parse
                    any_error = True
                    continue

                try:

                    submission = result.model_data["submission"]
                    if submission.curation_comment is None:
                        submission.curation_comment = ""

                    submission.curation_comment += "migrated from spreadsheet %s into CEDAR va pcor_tools" % source_file
                    migrated_json = self.reformat_json(result.model_data, target_version=target_version)

                    id = LoaderCedar.extract_id_for_resource(self.store_migrated(migrated_json))
                    model_json = json.loads(migrated_json)
                    name = model_json["RESOURCE_151"]["resource_name"]["@value"]
                    self.cedar_access.rename_resource(id, name)
                    result.template_current_location = name
                    logger.info("success for: %s" % name)

                except Exception as e:
                    logger.error('Error occurred: %s' % str(e))
                    result.success = False
                    pcor_error = PcorError()
                    pcor_error.type = ""
                    pcor_error.key = ""
                    pcor_error.message = str(e)
                    result.errors.append(pcor_error)


        return results
