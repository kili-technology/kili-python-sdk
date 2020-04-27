from ...helpers import format_result
from .queries import GQL_GET_PROJECT, GQL_GET_PROJECTS


class QueriesProject:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def get_projects(self, user_id: str, search_query: str = None, skip: int = 0, first: int = 100):
        """
        Get projects of user_id with a search_query

        Parameters
        ----------
        user_id : str
        search_query : str, optional (default = None)
            Returned projects have a title or a description that matches this string.
        skip : int, optional (default = 0)
            Number of projects to skip (they are ordered by their creation)
        first : int , optional (default = 100)
            Maximum number of projects to return

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'userID': user_id, 'searchQuery': search_query, 'skip': skip, 'first': first}
        result = self.auth.client.execute(GQL_GET_PROJECTS, variables)
        return format_result('data', result)


    def get_project(self, project_id: str):
        """
        Get project given its id

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return get_project(self.auth.client, project_id)


def get_project(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_PROJECT, variables)
    return format_result('data', result)