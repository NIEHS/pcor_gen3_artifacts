#!/usr/bin/env python3

# title           : upload_spreadsheet_watchdog
# description     : Monitor pcor_work_dir folder on ddn and trigger gen3 upload on arrival of new SS
# author          : Deep Patel
# env variable    : PROPERTIES_FILE=/path/to/properties_file
# usage           : python WebSubWd.py -f /path/to/pcor_work_dir/new
# python_version  : 3.9.16
# ====================================================================================================

import logging
import os
import sys
import time

from optparse import OptionParser
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import PatternMatchingEventHandler
from pcor_ingest.loader import Loader
from pcor_ingest.ingest_context import PcorIngestConfiguration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)

logger = logging.getLogger(__name__)


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.xlsm"]  # match only .xlsm files

    def process(self, event):
        source_path = event.src_path
        filename = os.path.basename(source_path)
        logger.info('\n\n_______________________________')
        logger.info('Event triggered: %s' % event.event_type)
        logger.info('Filename: %s' % filename)
        logger.info('Source Path: %s' % source_path)
        loader_ss = Loader(pcor_ingest_configuration=PcorIngestConfiguration(str(os.environ["PROPERTIES_FILE"])))
        loader_ss.process_pcor_load(loader_type='spreadsheet', file_path=source_path)

    def on_created(self, event):
        try:
            self.process(event)
        except Exception as ex:
            logger.error('\n\n\n\n Exception: {}'.format(ex))


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-f', "--folderPath", action='store', dest='folder_path')
    return parser.parse_args()[0]


def main():
    logger.info('Main function execution started.')
    global args
    args = setup_arguments()

    if "PROPERTIES_FILE" not in os.environ:
        logger.error("PROPERTIES_FILE not found in env. System exiting...")
        sys.exit()

    logger.info('Validate/Clean user passed arguments...')
    if len(sys.argv) > 1:
        folder_path = args.folder_path.rstrip('/')
        logger.info('Folder to be monitored :: %s' % folder_path)

        if not os.path.exists(folder_path):
            logger.error('ERROR: Folder to be monitored does not exists. System will exit now...')
            sys.exit()
        else:
            logger.info('Folder to be monitored exists.')
            observer = Observer()
            observer.schedule(MyHandler(), folder_path)
            observer.start()
            logger.info('Watchdog monitoring started...')

            try:
                while True:
                    sleep_time = 60
                    logger.info('Going to sleep for %d seconds.' % sleep_time)
                    time.sleep(sleep_time)
            except KeyboardInterrupt:
                observer.stop()
                logger.info('Watchdog monitoring stopped!')
            observer.join()
    else:
        logger.info('Arguments not satisfied!!!')


if __name__ == "__main__":
    main()
