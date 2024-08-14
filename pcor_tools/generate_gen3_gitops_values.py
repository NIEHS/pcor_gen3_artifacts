#!/usr/bin/env python3

# title           : generate_gen3_gitops_values
# description     : Generate 5 yaml values files for repo gen3-gitops using the content of custom_configs
# author          : Deep Patel
# usage           : python generate_gen3_gitops_values.py
# python_version  : 3.9.16
# ====================================================================================================

from jinja2 import Environment, FileSystemLoader
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

# Set the flag to True for AWS Staging(gen3-gitops)
AWS_STAGING_FLAG = False
if AWS_STAGING_FLAG:
    # Get the current month and day
    values_current_month_day = datetime.now().strftime("aws_values_%m_%d")
    gen3_gitops_values_path = os.path.join('../gen3-gitops', values_current_month_day)
else:
    gen3_gitops_values_path = '../gen3-gitops/values'

# Get the directory path of the custom_configs
custom_configs_path = '../custom_configs'
gen3_gitops_templates_path = '../gen3-gitops/templates'

# Load the Jinja2 environment with the script directory as the template folder
env = Environment(loader=FileSystemLoader(gen3_gitops_templates_path))

# Load the values.yaml template
etl_template = env.get_template('etl_template.j2')
fence_template = env.get_template('fence_template.j2')
guppy_template = env.get_template('guppy_template.j2')
portal_template = env.get_template('portal_template.j2')
values_template = env.get_template('values_template.j2')

try:
    # Create a new directory for gen3-gitops values if it does not exist
    if not os.path.exists(gen3_gitops_values_path):
        logger.info('Creating a new directory for gen3-gitops values at: %s' % gen3_gitops_values_path)
        os.makedirs(gen3_gitops_values_path)

    # Generate etl.yaml using the content of etlMapping.yaml file
    logger.info('\n\n=====================================================\n\n')
    logger.info('Generate etl.yaml using the content of etlMapping.yaml file')
    with open(os.path.join(custom_configs_path, 'etlMapping.yaml'), 'r') as etl_mapping_file:
        etl_mapping_content = etl_mapping_file.read()
        logger.debug('etl_mapping_content: \n%s' % etl_mapping_content)
        data = {
            'aws_staging': AWS_STAGING_FLAG,
            'etl_mapping_content': etl_mapping_content
        }
        rendered_etl_values = etl_template.render(data)
        logger.debug('rendered_etl_values: \n%s' % rendered_etl_values)
        with open(os.path.join(gen3_gitops_values_path, 'etl.yaml'), 'w') as etl_values_file:
            etl_values_file.write(rendered_etl_values)
            logger.info('etl.yaml file has been written successfully\n\n')

    # Generate fence.yaml using the content of user.yaml file
    logger.info('\n\n=====================================================\n\n')
    logger.info('Generate fence.yaml using the content of user.yaml file')
    with open(os.path.join(custom_configs_path, 'user.yaml'), 'r') as user_file:
        user_yaml_content = user_file.read()
        logger.debug('user_content: \n%s' % user_yaml_content)
    data = {
        'aws_staging': AWS_STAGING_FLAG,
        'user_yaml_content': user_yaml_content
    }
    rendered_user_values = fence_template.render(data)
    logger.debug('rendered_user_values: \n%s' % rendered_user_values)
    with open(os.path.join(gen3_gitops_values_path, 'fence.yaml'), 'w') as user_values_file:
        user_values_file.write(rendered_user_values)
        logger.info('fence.yaml file has been written successfully\n\n')

    # Generate guppy.yaml using the content of guppy.yaml file
    logger.info('\n\n=====================================================\n\n')
    logger.info('Generate guppy.yaml using the content of guppy.yaml file')
    with open(os.path.join(custom_configs_path, 'guppy.yaml'), 'r') as guppy_file:
        guppy_content = guppy_file.read()
        logger.debug('guppy_content: \n%s' % guppy_content)
    data = {
        'aws_staging': AWS_STAGING_FLAG,
        'guppy_content': guppy_content
    }
    rendered_guppy_values = guppy_template.render(data)
    logger.debug('rendered_guppy_values: \n%s' % rendered_guppy_values)
    with open(os.path.join(gen3_gitops_values_path, 'guppy.yaml'), 'w') as guppy_values_file:
        guppy_values_file.write(rendered_guppy_values)
        logger.info('guppy.yaml file has been written successfully\n\n')

    # Generate portal.yaml using the content of gitops.json and gitops.css files
    logger.info('\n\n=====================================================\n\n')
    logger.info('Generate portal.yaml using the content of gitops.json and gitops.css files')
    with open(os.path.join(custom_configs_path, 'gitops.json'), 'r') as gitops_json_file:
        gitops_json_content = gitops_json_file.read()
        logger.debug('gitops_json_content: \n%s' % gitops_json_content)
    with open(os.path.join(custom_configs_path, 'gitops.css'), 'r') as gitops_css_file:
        gitops_css_content = gitops_css_file.read()
        logger.debug('gitops_css_content: \n%s' % gitops_css_content)
    data = {
        'aws_staging': AWS_STAGING_FLAG,
        'gitops_json_content': gitops_json_content,
        'gitops_css_content': gitops_css_content
    }
    rendered_portal_values = portal_template.render(data)
    logger.debug('rendered_portal_values: \n%s' % rendered_portal_values)
    with open(os.path.join(gen3_gitops_values_path, 'portal.yaml'), 'w') as portal_values_file:
        portal_values_file.write(rendered_portal_values)
        logger.info('portal.yaml file has been written successfully\n\n')

    # Generate values.yaml
    logger.info('\n\n=====================================================\n\n')
    logger.info('Generate values.yaml')
    data = {
        'aws_staging': AWS_STAGING_FLAG
    }
    rendered_values = values_template.render(data)
    logger.debug('rendered_values: \n%s' % rendered_values)
    with open(os.path.join(gen3_gitops_values_path, 'values.yaml'), 'w') as values_file:
        values_file.write(rendered_values)
        logger.info('values.yaml file has been written successfully\n\n')

except Exception as e:
    logger.error("An error occurred: %s" % e)
