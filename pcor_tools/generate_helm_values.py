from jinja2 import Environment, FileSystemLoader
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

# Get the directory path of the custom_configs
custom_configs_path = '../custom_configs'

# Load the Jinja2 environment with the script directory as the template folder
env = Environment(loader=FileSystemLoader(custom_configs_path))

# Load the values.yaml template
values_template = env.get_template('values_template.j2')

try:
    # Read the content of user.yaml file
    with open(os.path.join(custom_configs_path, 'user.yaml'), 'r') as user_file:
        user_yaml_content = user_file.read()
        logger.debug('user_yaml_content: \n%s' % user_yaml_content)

    # Read the content of gitops.json file
    with open(os.path.join(custom_configs_path, 'gitops.json'), 'r') as gitops_file:
        gitops_content = gitops_file.read()
        logger.debug('gitops_content: \n%s' % gitops_content)

    # Read the content of etlMapping.yaml file
    with open(os.path.join(custom_configs_path, 'etlMapping.yaml'), 'r') as etl_mapping_file:
        etl_mapping_content = etl_mapping_file.read()
        logger.debug('etl_mapping_content: \n%s' % etl_mapping_content)

    # Define the data context for the template
    data = {
        'user_yaml_content': user_yaml_content,
        'gitops_content': gitops_content,
        'etl_mapping_content': etl_mapping_content
    }

    # Render the values.yaml template with the provided data
    rendered_values = values_template.render(data)
    logger.info('rendered_values \n%s:' % rendered_values)

    # Write the rendered content to a new file
    with open(os.path.join(custom_configs_path, 'auto_generated_values.yaml'), 'w') as combined_file:
        combined_file.write(rendered_values)
    logger.info("Combined YAML file generated.")

except Exception as e:
    logger.error("An error occurred: %s" % e)
