import logging
import os
import pandas as pd

from pcor_ingest.pcor_template_parser import PcorTemplateParser


logger = logging.getLogger(__name__)


class GeoSpatialDataResourceParser(PcorTemplateParser):
    """
        Parser subclass for geospatial data resource templates
    """

    def parse(self, template_absolute_path):
        """
        Parse a geospatial data resource
        :param template_absolute_path: absolute path to the template
        :return: PcorTemplateParseResult with parse result
        """

        df = pd.read_excel(template_absolute_path, sheet_name=0)

        # extract the program data