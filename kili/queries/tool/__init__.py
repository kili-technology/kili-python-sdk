import warnings

from ...helpers import format_result
from .queries import GQL_GET_TOOLS


def get_tools(client, project_id: str):
    message = """This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
    To retrieve jsonInterface, use:
        project = playground.get_project(project_id=project_id)
        json_interface = project['jsonInterface']
    """
    warnings.warn(message, DeprecationWarning)
