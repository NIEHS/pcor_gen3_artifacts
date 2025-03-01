import logging
import os
from datetime import datetime

from pcor_ingest.key_dataset_resource_parser import KeyDatasetResourceParser
from pcor_ingest.pcor_intermediate_model import PcorSubmissionInfoModel
from pcor_ingest.pcor_reporter import PcorReporter
from pcor_ingest.pcor_template_process_result import PcorProcessResult, PcorError
from pcor_ingest.pcor_template_processor import PcorTemplateProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class LoaderKeyDatasetsSpreadsheet:
    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.workspace_folder_path = None
        self.workspace_new_folder_path = None
        self.workspace_processing_folder_path = None
        self.workspace_processed_folder_path = None
        self.workspace_failed_folder_path = None
        self.pcor_reporter = PcorReporter(pcor_ingest_configuration)

    def validate_sub_folders(self, work_dir=None):
        # new files folder
        self.workspace_folder_path = work_dir
        self.workspace_new_folder_path = os.path.join(self.workspace_folder_path, 'new')

        # when loader is processing the file
        self.workspace_processing_folder_path = os.path.join(self.workspace_folder_path, 'processing')
        if not os.path.exists(self.workspace_processing_folder_path):
            os.mkdir(self.workspace_processing_folder_path)

        # when loader is processing the file successfully
        self.workspace_processed_folder_path = os.path.join(self.workspace_folder_path, 'processed')
        if not os.path.exists(self.workspace_processed_folder_path):
            os.mkdir(self.workspace_processed_folder_path)

        # when loader is processing the file failed
        self.workspace_failed_folder_path = os.path.join(self.workspace_folder_path, 'failed')
        if not os.path.exists(self.workspace_failed_folder_path):
            os.mkdir(self.workspace_failed_folder_path)

    def process_load(self, file_path=None):
        """
        Load a spreadsheet template for key datasets
        """
        logger.info('process_load()')
        logger.info('file_path dir: %s ' % file_path)
        file_name = os.path.abspath(file_path)
        work_dir = os.path.dirname(file_name)
        logger.info('work_dir dir: %s ' % work_dir)
        logger.info('file_path: %s' % file_path)
        #self.validate_sub_folders(work_dir=work_dir)

        file = os.path.basename(file_path)

        if file.endswith('.xlsx'):
            logger.info('Spreadsheet found: %s' % file)
        else:
            raise Exception("input is not a valid spreadsheet type")

        # new folder
        #file_path = os.path.join(self.workspace_new_folder_path, file)
        #new_file_name = LoaderKeyDatasetsSpreadsheet.add_timestamp_to_file(file)
        #processing_file_path = self.workspace_processing_folder_path + '/' + new_file_name
        #logger.info(
        #    '\nMoving file: %s \nsrc: %s\ndst: %s' % (
        #        file, file_path, self.workspace_processing_folder_path))
        #shutil.move(src=file_path, dst=processing_file_path)

        # processing folder
        results = []

        ss_reader = KeyDatasetResourceParser(self.pcor_ingest_configuration)

        any_error = False

        # parse is going to build an array of results, as the spreadheet contains multiple curated data sets

        try:
            ss_reader.parse(file_path, results)  # took result out and made a param
        except Exception as e:
            logger.error('Error occurred: %s' % str(e))
            any_error = True
            result = PcorProcessResult()
            submission = PcorSubmissionInfoModel()
            submission.curator_email = self.pcor_ingest_configuration.submitter_email
            submission.template_source = file_path
            result.model_data["submission"] = submission
            result.success = False
            pcor_error = PcorError()
            pcor_error.type = ""
            pcor_error.key = ""
            pcor_error.message = str(e)
            result.errors.append(pcor_error)

        if not any_error:

            logger.info("no parse error, continue with processing")
            # do the processing stuff here for a template
            process_template = PcorTemplateProcessor(pcor_ingest_configuration=self.pcor_ingest_configuration)

            for result in results:

                if not result.success: # skip things that didn't parse
                    any_error = True
                    continue

                try:
                    #logger.debug("result:{}", result)
                    process_template.process(result)

                except Exception as e:
                    logger.error('Error occurred: %s' % str(e))
                    result.success = False
                    pcor_error = PcorError()
                    pcor_error.type = ""
                    pcor_error.key = ""
                    pcor_error.message = str(e)
                    result.errors.append(pcor_error)

        for result in results:
            self.pcor_reporter.report(result)

        return results

    @staticmethod
    def add_timestamp_to_file(file_name):
        # test1~pcor~_23_06_29_124427.xlsm
        try:
            idx = file_name.index('~pcor~')
            file_part = file_name[0:idx]
            new_file_name = file_part + '~pcor~' + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm'
            return new_file_name
        except ValueError:
            new_file_name = file_name.replace('.xlsm', '~pcor~'
                                              + str(datetime.now().strftime('_%y_%m_%d_%H%M%S')) + '.xlsm')
            logger.info("new file name:%s" % new_file_name)
            return new_file_name
