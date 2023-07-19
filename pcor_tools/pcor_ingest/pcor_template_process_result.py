class PcorProcessResult:
    """
    Result of processing a template
    """

    def __init__(self):
        self.success = True
        # specific to the item being added
        self.id = ""
        self.type = ""
        self.submitter_id = ""
        self.resource_name = ""
        # parsed model information
        self.model_data = {}
        self.message = ""
        self.errors = [] # errors in processing that are not validation errors from Gen3
        # general contextual information
        self.project_id = ""
        self.project_code = ""
        self.project_name = ""
        self.program_submitter_id = ""
        self.program_name = ""
        # error information
        self.path_url = ""
        self.response_content = ""
        self.request_content = ""
        self.template_source = ""
        self.template_current_location = ""


class PcorError:
    """
    Represents details of an error
    """

    def __init__(self):
        self.type = ""
        self.key = ""
        self.message = ""




