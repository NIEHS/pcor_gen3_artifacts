import logging
import traceback
import warnings
import pandas as pd
from pcor_ingest.pcor_intermediate_model import PcorGeoToolModel
from pcor_ingest.pcor_template_parser import PcorTemplateParser

logger = logging.getLogger(__name__)


class GeoSpatialToolResourceParser(PcorTemplateParser):
    """
        Parser subclass for geospatial tool resource templates
    """
    def parse(self, template_absolute_path, result):
        """
        Parse a geospatial tool resource
        :param template_absolute_path: absolute path to the template
        :param result: PcorTemplateParseResult with parse result
        """
        super(GeoSpatialToolResourceParser, self).parse(template_absolute_path, result)
        result.type = "geospatial_tool_resource"
        warnings.simplefilter(action='ignore', category=UserWarning)
        df = pd.read_excel(template_absolute_path, sheet_name=0)
        try:
            detail_model = self.extract_resource_details(df)
            result.model_data["geospatial_tool_resource"] = detail_model
            result.resource_detail_guid = detail_model.resource_submitter_id
        except AttributeError as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.message = err
        except Exception as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.traceback = traceback.format_exc(err)
            result.message = err
        logger.info("returning general parsed data: %s" % result)

    def extract_resource_details(self, template_df):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the GeoExposure_Tool_Resource stanza")
        geo_resource = PcorGeoToolModel()

        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Tool_Resource':
                logging.debug("found Tool_Resource/GeoExposure_Tool_Resource ")
                for j in range(i, ss_rows):
                    logger.info('prop name: %s' % template_df.iat[j, 0])
                    if template_df.iat[j,0] == 'tool_type':
                        geo_resource.tool_type = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'intended_use':
                        geo_resource.intended_use = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'is_open':
                        geo_resource.isOpen = \
                            PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if str(geo_resource.isOpen).lower() == 'no' or str(
                                geo_resource.isOpen).lower() == 'none':
                            geo_resource.isOpen = False
                        if str(geo_resource.isOpen).lower() == 'yes':
                            geo_resource.isOpen = True

        return geo_resource
