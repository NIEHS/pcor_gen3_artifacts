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




