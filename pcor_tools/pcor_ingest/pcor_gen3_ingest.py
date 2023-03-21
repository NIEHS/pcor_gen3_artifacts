import logging

logger = logging.getLogger(__name__)


class PcorGen3Ingest:
    """
    Library for ingesting data into PCOR
    """

    def ingest_project(self, pcor_ingest_configuration, pcor_intermediate_project_model):
        """
        Ingest a project, will create the project if it does not exist
        :param ingest_context: IngestContext with information to connect to Gen3
        :param pcor_intermediate_project_model: PcorIntermediateProjectModel with project data to add or update
        :return: PcorIntermediateProjectModel that will have id and submitter id provisioned
        """
        logger.info('ingest_project')



