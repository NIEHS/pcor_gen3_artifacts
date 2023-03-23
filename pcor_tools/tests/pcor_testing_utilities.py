from pcor_ingest.ingest_context import PcorIngestConfiguration


def get_pcor_ingest_configuration():
    """Get the ingest configuration appropriate for unit tests against a local docker-compose instance"""
    testing_configuration=PcorIngestConfiguration('pcor_test1.properties')




