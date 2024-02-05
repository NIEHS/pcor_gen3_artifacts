import sys
from optparse import OptionParser

from jinja2 import Environment, FileSystemLoader
import pandas as pd
import os
import logging
"""
Generates user.yaml file from template based on an input of user/program/project
"""
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

# Get the directory path of the custom_configs
custom_configs_path = '../custom_configs'


def setup_arguments():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output')
    return parser.parse_args()[0]


def main():
    logger.info('Main function execution started.')
    global args
    global opts
    args = setup_arguments()

    input_file = args.input
    output_file = args.output

    # Load the Jinja2 environment with the script directory as the template folder
    env = Environment(loader=FileSystemLoader(custom_configs_path))

    # Load the values.yaml template
    values_template = env.get_template('user_template.j2')

    # hash of programs and projects[] gives unique programs
    programs_and_projects_dict = {}
    # hash of users - to handle duplicates

    try:

        # read in the data csv file (program,project)
        df = pd.read_csv(input_file)
        ss_rows = df.shape[0]

        # for each row start breaking out the data for the structures I need in the template. Uses
        # dictionaries to handle duplicate or out of order data

        # user { program [project]} to organize programs and projects

        for i in range(ss_rows):

            program = df.iat[i, 0]
            project = df.iat[i, 1]

            logger.info("program: %s project: %s" % (program, project))

            if program in programs_and_projects_dict:
                if project not in programs_and_projects_dict[program]:
                    programs_and_projects_dict[program].append(project)
            else:
                programs_and_projects_dict[program] = [project]



        # Define the data context for the template
        data = {
            'programs_and_projects': programs_and_projects_dict,
            'users': user_dict
        }

        # Render the values.yaml template with the provided data
        rendered_values = values_template.render(data)
        logger.info('rendered_values \n%s:' % rendered_values)

        # Write the rendered content to a new file
        with open(os.path.join(custom_configs_path, 'user.yaml'), 'w') as combined_file:
            combined_file.write(rendered_values)

        with open(os.path.join(custom_configs_path, 'auto_generated_values_local.yaml'), 'w') as combined_file:
            combined_file.write(rendered_values_local)

        logger.info("Combined YAML file generated.")

    except Exception as e:
        logger.error("An error occurred: %s" % e)
