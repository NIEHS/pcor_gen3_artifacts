import logging
import traceback
import warnings
import pandas as pd
from pcor_ingest.pcor_intermediate_model import PcorGeospatialDataResourceModel
from pcor_ingest.pcor_template_parser import PcorTemplateParser

logger = logging.getLogger(__name__)


class GeoSpatialDataResourceParser(PcorTemplateParser):
    """
        Parser subclass for geospatial data resource templates
    """

    def __init__(self, pcor_ingest_configuration):
        super().__init__(pcor_ingest_configuration)

    def parse(self, template_absolute_path, result):
        """
        Parse a geospatial data resource
        :param template_absolute_path: absolute path to the template
        :param result: PcorTemplateParseResult with parse result
        """
        super(GeoSpatialDataResourceParser, self).parse(template_absolute_path, result)
        result.type = "geospatial_data_resource"
        warnings.simplefilter(action='ignore', category=UserWarning)
        df = pd.read_excel(template_absolute_path, sheet_name=0, engine='openpyxl')
        try:
            detail_model = self.extract_resource_details(df)
            result.model_data["geospatial_data_resource"] = detail_model
            result.resource_detail_guid = detail_model.resource_submitter_id
        except AttributeError as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.message = str(err)
        except Exception as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.traceback = traceback.format_exc()
            result.message = str(err)
        logger.info("returning general parsed data: %s" % result)

    def extract_resource_details(self, template_df):
        """
        Given a pandas dataframe with the template date, extract out the resource related data
        :param template_df: pandas df of the spreadsheet
        :return: PcorProjectModel with project data from ss
        """

        # loop thru the template until the marker 'PROGRAM' is found

        ss_rows = template_df.shape[0]
        logging.debug("iterate looking for the GeoExposure_Data_Resource stanza")
        geo_resource = PcorGeospatialDataResourceModel()
        geo_resource.display_type = "GeoExposureData"
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Data_Resource':
                # Data Resource section
                logging.debug("found Data_Resource/GeoExposure_Data_Resource ")
                for j in range(i, ss_rows):
                    logger.info('prop name: %s  value: %s' % (template_df.iat[j, 0], template_df.iat[j, 1]))
                    if template_df.iat[j, 0] == 'comments':
                        geo_resource.comments = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'intended_use':
                        geo_resource.intended_use = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'source_name':
                        geo_resource.source_name = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'update_frequency':
                        geo_resource.update_frequency = PcorTemplateParser.camel_case_it(
                            PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'includes_citizen_collected':
                        geo_resource.includes_citizen_collected = \
                            PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if str(geo_resource.includes_citizen_collected).lower() == 'no' or str(
                                geo_resource.includes_citizen_collected).lower() == 'none':
                            geo_resource.includes_citizen_collected = False
                        if str(geo_resource.includes_citizen_collected).lower() == 'yes':
                            geo_resource.includes_citizen_collected = True
                    elif template_df.iat[j, 0] == 'has_api':
                        geo_resource.has_api = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if str(geo_resource.has_api).lower() == 'no' or str(geo_resource.has_api).lower() == 'none':
                            geo_resource.has_api = False
                        if str(geo_resource.has_api).lower() == 'yes':
                            geo_resource.has_api = True
                    elif template_df.iat[j, 0] == 'has_visualization_tool':
                        geo_resource.has_visualization_tool = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if str(geo_resource.has_visualization_tool).lower() == 'no' or \
                                str(geo_resource.has_visualization_tool).lower() == 'none':
                            geo_resource.has_visualization_tool = False
                        if str(geo_resource.has_visualization_tool).lower() == 'yes':
                            geo_resource.has_visualization_tool = True
                    # GeoExposure_Data_Resource section
                    elif template_df.iat[j, 0] == 'measures':
                        measures = PcorTemplateParser.make_complex_camel_case_array(template_df.iat[j, 1])
                        measures_rollup = self.pcor_measures_rollup.process_measures(measures)
                        geo_resource.measures = measures_rollup.measures
                        geo_resource.measures_parent = measures_rollup.measures_parents
                        geo_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
                        geo_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor
                    elif template_df.iat[j, 0] == 'measurement_method':
                        geo_resource.measurement_method = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'measurement_method_other':
                        temp_measurement_method_other = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                        geo_resource.measurement_method = PcorTemplateParser.combine_prop(geo_resource.measurement_method, temp_measurement_method_other)
                    elif template_df.iat[j, 0] == 'time_extent_start':
                        time_extent_start = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if time_extent_start is not None:
                            geo_resource.time_extent_start_yyyy = PcorTemplateParser.format_date_time(time_extent_start)
                    elif template_df.iat[j, 0] == 'time_extent_end':
                        geo_resource.time_extent_end = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if geo_resource.time_extent_end is not None:
                            if geo_resource.time_extent_end.lower() == "current":
                                geo_resource.time_extent_end = 'Current'
                            else:
                                geo_resource.time_extent_end = str(self.formate_date_time(geo_resource.time_extent_end))
                    elif template_df.iat[j, 0] == 'time_available_comment':
                        geo_resource.time_available_comment = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'temporal_resolution':
                        geo_resource.temporal_resolution = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'spatial_resolution':
                        geo_resource.spatial_resolution = PcorTemplateParser.camel_case_it(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'spatial_resolution_other':
                        temp_spatial_resolution_other = PcorTemplateParser.camel_case_it(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                        geo_resource.spatial_resolution = PcorTemplateParser.combine_prop(geo_resource.spatial_resolution, temp_spatial_resolution_other)
                    elif template_df.iat[j, 0] == 'spatial_coverage':
                        geo_resource.spatial_coverage = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'spatial_coverage_specific_regions':
                        geo_resource.spatial_coverage_specific_regions = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'spatial_bounding_box':
                        geo_resource.spatial_bounding_box = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'geometry_type':
                        geo_resource.geometry_type = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'geometry_source':
                        geo_resource.geometry_source = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'model_methods':
                        geo_resource.model_methods = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'exposure_media':
                        geo_resource.exposure_media = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'geographic_feature':
                        geo_resource.geographic_feature = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'geographic_feature_other':
                        temp_geographic_feature_other = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                        geo_resource.geographic_feature = PcorTemplateParser.combine_prop(geo_resource.geographic_feature, temp_geographic_feature_other)
                    elif template_df.iat[j, 0] == 'data_formats':
                        geo_resource.data_formats = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'data_location':
                        geo_resource.data_location = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])

        return geo_resource
