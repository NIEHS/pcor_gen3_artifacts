import logging
import os
import pandas as pd

from pcor_ingest.pcor_intermediate_model import PcorGeospatialDataResourceModel
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
        # parseresult = super.parse(template_absolute_path)
        # add details data to parseresult
        #df = pd.read_excel(template_absolute_path, sheet_name=0)

        # extract the program data


    @staticmethod
    def extract_resource_details(template_df):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the RESOURCE DETAILS stanza")
        geo_resource = PcorGeospatialDataResourceModel()

        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'RESOURCE DETAILS':
                logging.debug("found RESOURCE DETAILS")
                for j in range(i, ss_rows):
                    if template_df.iat[j, 0] == 'temporal resolution':
                        geo_resource.temporal_resolution = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'measures':
                        for k in range(1, template_df.shape[1]):
                            val = template_df.iat[j, k]
                            if val:
                                geo_resource.measures.append(val)
                            else:
                                break

        return geo_resource
