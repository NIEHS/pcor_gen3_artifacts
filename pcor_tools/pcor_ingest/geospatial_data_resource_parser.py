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
        parse_result = super(GeoSpatialDataResourceParser, self).parse(template_absolute_path)
        df = pd.read_excel(template_absolute_path, sheet_name=0)
        try:
            parse_result.model_data["geospatial_data_resource"] = self.extract_resource_details(df)
        except Exception as err:
            logger.error("exception parsing resource details: %s" % err)
            parse_result.success = False
            parse_result.errors.append("error parsing resource details: %s" % err)
            return parse_result

        logger.info("returning general parsed data: %s" % parse_result)
        return parse_result

    @staticmethod
    def extract_resource_details(template_df):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the GeoExposure_Data_Resource stanza")
        geo_resource = PcorGeospatialDataResourceModel()

        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'GeoExposure_Data_Resource':
                logging.debug("found GeoExposure_Data_Resource ")
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
