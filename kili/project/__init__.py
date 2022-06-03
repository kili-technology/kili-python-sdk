"""Project module."""


class Project:  # pylint: disable=too-few-public-methods
    """
    Object that represents a project in Kili.
    It allows management operations such as uploading assets, uploading predictions,
    modifying the project's queue etc.
    It also allows queries from this project such as its assets, labels etc.
    """

    def __init__(self, client, project_id, input_type, title):
        self.project_id = project_id
        self.client = client
        self.title = title
        self.input_type = input_type
