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
            if template_df.iat[i, 0] == 'Data_Resource':
                logging.debug("found Data_Resource/GeoExposure_Data_Resource ")
                for j in range(i, ss_rows):
                    # FixMe:  data_type is missing in schema!
                    if template_df.iat[j, 0] == 'data_type':
                        geo_resource.data_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'comments':
                        geo_resource.comments = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'intended_use':
                        geo_resource.intended_use = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'source_name':
                        geo_resource.source_name = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'update_frequency':
                        geo_resource.update_frequency = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'includes_citizen_collected':
                        geo_resource.includes_citizen_collected = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'has_api':
                        geo_resource.has_api = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'has_visualization_tool':
                        geo_resource.has_visualization_tool = template_df.iat[j, 1]

                    # GeoExposure_Data_Resource section
                    elif template_df.iat[j, 0] == 'measures':
                        geo_resource.measures = template_df.iat[j, 1].split(',')
                    elif template_df.iat[j, 0] == 'measurement_method':
                        geo_resource.measurement_method = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'time_extent_start':
                        geo_resource.time_extent_start = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'time_extent_end':
                        geo_resource.time_extent_end = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'time_available_comment':
                        geo_resource.time_available_comment = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'temporal_resolution':
                        geo_resource.temporal_resolution = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'spatial_resolution':
                        geo_resource.spatial_resolution = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'spatial_coverage':
                        geo_resource.spatial_coverage = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'spatial_coverage_specific_regions':
                        geo_resource.spatial_coverage_specific_regions = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'spatial_bounding_box':
                        geo_resource.spatial_bounding_box = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'geometry_type':
                        geo_resource.geometry_type = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'geometry_source':
                        geo_resource.geometry_source = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'model_methods':
                        geo_resource.model_methods = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'exposure_media':
                        geo_resource.exposure_media = template_df.iat[j, 1]
                    elif template_df.iat[j, 0] == 'geographic_feature':
                        geo_resource.geographic_feature = template_df.iat[j, 1]

        return geo_resource
