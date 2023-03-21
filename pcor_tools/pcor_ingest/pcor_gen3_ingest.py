import logging

from gen3.submission import Gen3Submission
from pcor_ingest.gen3auth import PcorGen3Auth

logger = logging.getLogger(__name__)


class PcorGen3Ingest:
    """
    Library for ingesting data into PCOR
    """

    def __int__(self, pcor_ingest_configuration, gen3_auth=None):
        """
        Initialize ingest tool
        :param pcor_ingest_configuration: IngestConfiguration with Gen3 server properties
        :param gen3_auth: Optional Gen3Auth object if auth is done
        :return:
        """

        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.gen3_auth = gen3_auth

        if not gen3_auth:
            logger.info('doing auth')
            gen3_auth = PcorGen3Auth(pcor_ingest_configuration)
            self.gen3_auth = gen3_auth
            logger.info("authenticated to Gen3")

    def create_project(self, program, pcor_intermediate_project_model):
        """
        :param program: identifier of the program in Gen3
        :param pcor_intermediate_project_model: data structure representing project data
        :return: string or gen3 response dictionary
        """
        logger.info('create_project()')
        sub = Gen3Submission(self.auth)
        project = pcor_intermediate_project_model.project_name

        existing_projects = self.get_projects(program)
        project_already_exist = self.check_project_exists(existing_projects, project)
        if project_already_exist:
            logger.info('Project already exists: %s', project)
            return 'project already exists'
        else:
            logger.info('Creating project: %s', project)
            response = sub.create_project(program, json)
            return response

    #############################################
    # supporting methods
    ###########################################

    def check_project_exists(self, existing_projects, project):
        project_already_exist = False
        if existing_projects and 'links' in existing_projects:
            for entry in existing_projects['links']:
                temp_project = entry.split('/')[-1]
                if temp_project == project:
                    project_already_exist = True
        return project_already_exist

    def retrieve_project_files_tsv(self, project, program, node_type, export_file):
        """
        Export the nodes as tsv
        :param project: project identifier
        :param program: program identifier
        :param node_type: type of Gen3 node
        :param export_file: location of downloaded file
        :return: export file
        """
        logger.info('retrieve_project_files_tsv()')
        sub = Gen3Submission(self.auth)
        sub.export_node(program, project, node_type, "tsv", filename=export_file)

    def get_projects(self, program=None):
        """
        :param program: GEN3 program defaults to one in property file
        :return: dict of projects with project links
        """
        logger.info('get_projects()')
        if program is None:
            program = self.program
        sub = Gen3Submission(self.auth)
        projects = sub.get_projects(program)
        return projects

    def get_individual_project_info(self, project_code):
        """
        Do a query to get code, id, and name of a project based on the project code
        :param project_code: code field in project
        :return: JSON with query result
        """

        json = """{{
         project(code: "{}") {{
           id
           code
           dbgap_accession_number
           submitter_id
           name
         }}
       }}
       """.format(project_code)
        logger.info("query:{}".format(json))

        sub = Gen3Submission(self.auth)
        result = sub.query(json)
        logger.info("result:{}".format(result))
        return result

    def submit_record(self, program, project, json):
        """
        :param program: The program to submit to.
        :param project: The project to submit to.
        :param json: The json defining the record(s) to submit. For multiple records, the json should be an
        array of records.
        :return:
        """
        logger.info('submit_record()')
        sub = Gen3Submission(self.auth)
        submission_status = sub.submit_record(program, project, json)
        return submission_status





