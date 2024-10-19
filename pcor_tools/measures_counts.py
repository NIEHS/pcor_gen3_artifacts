import os
import json
import logging
import re
import shutil
import sys
from optparse import OptionParser

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

def setup_arguments():
    parser = OptionParser()
    parser.add_option('-o', "--output", action='store', dest='output_file', default=None)
    parser.add_option('-i', "--input", action='store', dest='input_file', default=None)

    return parser.parse_args()[0]

def process_measures(measures, json_elements):
    resc_count = 0
    for measure in json_elements:
        resc_count += 1

        for element in measure["measures"]:
            tally = measures.get(element)
            if tally:
                measures[element] = tally + 1
            else:
                measures[element] = 1

    return resc_count


def output_measures(measures, output_file):
    logger.info(f"Writing measures {measures}")
    for measure in measures:
        print(f"{measure},{measures[measure]}", file=output_file)

def main():

    global args
    args = setup_arguments()
    input = args.input_file
    output = args= args.output_file
    measures = {}
    resc_count = 0

    if not os.path.exists(input):
        sys.exit()
    else:
        logger.info('input: %s' % input)
    with open(output, 'w') as o:
        with open(input, 'r') as f:
            contents_json = json.loads(f.read())

            geospatial_measures = contents_json['data']['geospatial_data_resource']
            resc_count += process_measures(measures, geospatial_measures)

            pop_measures = contents_json['data']['population_data_resource']
            resc_count += process_measures(measures, pop_measures)

            key_measures = contents_json['data']['key_data_resource']
            resc_count += process_measures(measures, key_measures)

        output_measures(measures, o)
        logger.info("resc_count: %d" % resc_count)

if __name__ == "__main__":
    main()
