import logging
import traceback
import warnings
import pandas as pd
from pcor_ingest.pcor_intermediate_model import PcorPopDataResourceModel
from pcor_ingest.pcor_template_parser import PcorTemplateParser

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)


class PopulationDataResourceParser(PcorTemplateParser):
    """
        Parser subclass for population data resource templates
    """

    def __init__(self, pcor_ingest_configuration):
        super().__init__(pcor_ingest_configuration)

    def parse(self, template_absolute_path, result):
        """
        Parse a geospatial data resource
        :param template_absolute_path: absolute path to the template
        :param result: PcorTemplateParseResult with parse result
        """
        super(PopulationDataResourceParser, self).parse(template_absolute_path, result)
        result.type = "population_data_resource"
        warnings.simplefilter(action='ignore', category=UserWarning)
        df = pd.read_excel(template_absolute_path, sheet_name=0, engine='openpyxl')
        try:
            detail_model = self.extract_resource_details(df)
            result.model_data["population_data_resource"] = detail_model
            result.resource_detail_guid = detail_model.resource_submitter_id
        except AttributeError as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.message = err
        except Exception as err:
            logger.error("exception parsing resource details: %s" % err)
            result.success = False
            result.traceback = traceback.format_exc()
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
        logging.debug("iterate looking for the GeoExposure_Data_Resource stanza")
        pop_resource = PcorPopDataResourceModel()
        pop_resource.display_type = "PopulationData"
        for i in range(ss_rows):
            if template_df.iat[i, 0] == 'Data_Resource':
                # Data Resource section
                logging.debug("found Data_Resource/Population_Data_Resource ")
                for j in range(i, ss_rows):
                    logger.info('prop name: %s  value: %s' % (template_df.iat[j, 0], template_df.iat[j, 1]))
                    if template_df.iat[j, 0] == 'comments':
                        pop_resource.comments = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'intended_use':
                        pop_resource.intended_use = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'source_name':
                        pop_resource.source_name = PcorTemplateParser.make_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'update_frequency':
                        pop_resource.update_frequency = PcorTemplateParser.camel_case_it(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'includes_citizen_collected':
                        pop_resource.includes_citizen_collected = PcorTemplateParser.sanitize_boolean(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'has_api':
                        pop_resource.has_api = PcorTemplateParser.sanitize_boolean(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'has_visualization_tool':
                        pop_resource.has_visualization_tool = PcorTemplateParser.sanitize_boolean(template_df.iat[j, 1])
                    # Population_Data_Resource section
                    elif template_df.iat[j, 0] == 'exposures':
                        pop_resource.exposures = PcorTemplateParser.make_complex_camel_case_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'exposure_media':
                        pop_resource.exposure_media = PcorTemplateParser.make_complex_camel_case_array(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'measures':
                        measures = PcorTemplateParser.make_complex_array(template_df.iat[j, 1])
                        measures_rollup = self.pcor_measures_rollup.process_measures(measures)
                        pop_resource.measures = measures_rollup.measures
                        pop_resource.measures_parent = measures_rollup.measures_parents
                        pop_resource.measures_subcategory_major = measures_rollup.measures_subcategories_major
                        pop_resource.measures_subcategory_minor = measures_rollup.measures_subcategories_minor
                    elif template_df.iat[j, 0] == 'outcomes':
                        pop_resource.outcomes = PcorTemplateParser.make_complex_camel_case_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'outcomes_other':
                        temp_outcomes_other = PcorTemplateParser.make_complex_camel_case_array(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                        pop_resource.outcomes = PcorTemplateParser.combine_prop(pop_resource.outcomes, temp_outcomes_other)
                    elif template_df.iat[j, 0] == 'time_extent_start':
                        time_extent_start = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if time_extent_start is not None:
                            pop_resource.time_extent_start_yyyy = PcorTemplateParser.format_date_time(time_extent_start)
                    elif template_df.iat[j, 0] == 'time_extent_end':
                        time_extent_end = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                        if time_extent_end is not None:
                            pop_resource.time_extent_end_yyyy = PcorTemplateParser.format_date_time(time_extent_end)
                    elif template_df.iat[j, 0] == 'time_available_comment':
                        pop_resource.time_available_comment = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'temporal_resolution':
                        pop_resource.temporal_resolution = PcorTemplateParser.sanitize_column(template_df.iat[j, 1])
                    elif template_df.iat[j, 0] == 'spatial_resolution':
                        pop_resource.spatial_resolution = PcorTemplateParser.camel_case_it(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    #elif template_df.iat[j, 0] == 'spatial_resolution_other': FIXME: decide how to handle other
                    #    temp_spatial_resolution_other = PcorTemplateParser.camel_case_it(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    #    pop_resource.spatial_resolution = PcorTemplateParser.combine_prop(pop_resource.spatial_resolution, temp_spatial_resolution_other)
                    elif template_df.iat[j, 0] == 'spatial_coverage':
                        pop_resource.spatial_coverage = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'spatial_coverage_specific_regions':
                        pop_resource.spatial_coverage_specific_regions = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(
                            template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'geometry_type':
                        pop_resource.geometry_type = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'geometry_source':
                        pop_resource.geometry_source = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'model_methods':
                        pop_resource.model_methods = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'population_studied':
                        pop_resource.population_studied = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(
                            template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'population_studied_other':
                        temp_population_studied_other = PcorTemplateParser.make_array_and_camel_case(PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                        pop_resource.population_studied = PcorTemplateParser.combine_prop(pop_resource.population_studied, temp_population_studied_other)
                    elif template_df.iat[j, 0] == 'data_formats':
                        pop_resource.data_formats = PcorTemplateParser.make_array_and_camel_case(
                            PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))
                    elif template_df.iat[j, 0] == 'data_location':
                        pop_resource.data_location = PcorTemplateParser.make_array(
                            PcorTemplateParser.sanitize_column(template_df.iat[j, 1]))

        return pop_resource
