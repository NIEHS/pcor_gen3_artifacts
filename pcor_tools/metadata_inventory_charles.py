import json
import logging
import os
import sys
from io import TextIOWrapper
from optparse import OptionParser

from pcor_cedar.cedar_backup_visitor_processor import CedarBackupVisitor, CedarBackupVisitorProcessor
from pcor_ingest.measures_rollup import PcorMeasuresRollup

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

class MetadataInventory:
    
    def __init__(self, measure:str, measure_sub_minor:str, measure_sub_major:str, resource_title:str,
                 resource_description:str, exposures):
        self.measure = measure
        self.resource_title = resource_title
        self.resource_description = resource_description
        self.measure_sub_minor = measure_sub_minor
        self.measure_sub_major = measure_sub_major
        self.exposures = exposures
        
    def to_csv(self):
            # Replace commas with a safe character or remove them

            safe_title = str(self.resource_title).replace(',', '')
            safe_description = str(self.resource_description).replace(',', '')
            exposure_list = ""
            for i, exposure in enumerate(self.exposures):
                exposure_list += exposure
                if i < len(self.exposures)-1:
                    exposure_list += ","

            return f"{self.measure},{self.measure_sub_minor},{self.measure_sub_major},{safe_title},{safe_description},{exposure_list}"


class MetadataInventoryVisitor(CedarBackupVisitor):
    """
    Visitor class for collecting metadata inventory from a Cedar backup.
    """

    def __init__(self, output_file:TextIOWrapper):
        """
        Create visitor with a given output file.
        :param pcor_measures_rollup rollup of measures
        :type pcor_measures_rollup: PcorMeasuresRollup
        :param output_file: file that will be written to with inventory data.
        :type output_file: TextIOWrapper with a file opened for writing that will receive the inventory data.
        """
        super().__init__()
        self.output_file = output_file

    def visit(self, cedar_model: dict, file_name: str, pcor_measures_rollup: PcorMeasuresRollup):
        logger.info(f"visit cedar data:{cedar_model}")
        resource_title = cedar_model["resource"].name
        resource_description = cedar_model["resource"].description

        exposures = []
        measures = []
        measures_sub_minor = []
        measures_sub_major = []


        if cedar_model.get("population_data_resource", None):
            measures = cedar_model["population_data_resource"].measures
            exposures = cedar_model["population_data_resource"].exposures
        elif cedar_model.get("geospatial_data_resource", None):
            measures = cedar_model["geospatial_data_resource"].measures
        elif cedar_model.get("key_dataset", None):
            measures = cedar_model["key_dataset"].measures
            exposures = cedar_model["key_dataset"].exposure_media
        else:
            return


        for i, measure in enumerate(measures):
            measures_rollup_value = pcor_measures_rollup.lookup_measure(measure)
            inventory_item = MetadataInventory(measure, measures_rollup_value.subcategory_minor, measures_rollup_value.subcategory_major,
                                               resource_title,
                 resource_description, exposures)
            self.output_file.write(inventory_item.to_csv()+"\n")


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-i', "--input_directory", action='store', dest='input_directory', default=None)
    parser.add_option('-o', "--output_file", action='store', dest='output_file', default=None)

    return parser.parse_args()[0]

def main():
    logger.info('Main function execution started. Processing a CEDAR local directory tree')
    global args
    args = setup_arguments()

    input_directory = args.input_directory
    output_file = args.output_file

    if not input_directory:
        logger.error("no input_directory, specify this parameter with -i")
        raise Exception("no -i parameter specified")

    if not output_file:
        logger.error("no output_file, specify this parameter with -o")
        raise Exception("no -t parameter specified")

    logger.info(f"input_directory: {input_directory}")
    logger.info(f"output_file: {output_file}")

    if not os.path.exists(input_directory):
        logger.error(f"Input directory '{input_directory}' does not exist.")
        sys.exit(1)

    # Check if output file already exists
    if os.path.exists(output_file):
        logger.error(
            f"Output file '{output_file}' already exists. Please specify a different output path or remove the existing file.")
        sys.exit(1)

    with open(output_file, "w") as output_as_file:
        my_visitor = MetadataInventoryVisitor(output_as_file)
        processor = CedarBackupVisitorProcessor(my_visitor, input_directory)
        processor.start()


if __name__ == "__main__":
    main()
