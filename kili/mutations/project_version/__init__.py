from typing import Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result
from .queries import (GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION)

class MutationsProjectVersion:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v2'])
    @typechecked
    def update_properties_in_project_version(self, project_version_id: str, 
            content: Optional[str]):
        """
        Update properties of a project version

        Parameters
        ----------
        - project_version_id : str
            Identifier of the project version
        - content : Optional[str]
            Link to download the project version

        Returns
        -------
        - a result object which indicates if the mutation was successful.

        Examples
        -------
        >>> kili.update_properties_in_project_version(project_version_id=project_version_id, content='test')
        """
        variables = {
            'content': content,
            'id': project_version_id,
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION, variables)
        return format_result('data', result)