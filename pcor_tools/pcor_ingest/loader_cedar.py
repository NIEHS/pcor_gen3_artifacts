import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class LoaderCedar:
    def __init__(self):
        pass

    def process_load(self):
        pass