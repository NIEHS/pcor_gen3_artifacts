import os

from pcor_ingest.ingest_context import PcorIngestConfiguration


def get_pcor_ingest_configuration():
    """Get the ingest configuration appropriate for unit tests against a local docker-compose instance"""
    env_config_file = os.getenv('PCOR_GEN3_CONFIG_LOCATION')
    if not env_config_file:
       env_config_file = 'test_resources/pcor.properties'

    testing_configuration = PcorIngestConfiguration(env_config_file)
    return testing_configuration
