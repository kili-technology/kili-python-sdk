from ...helpers import deprecate, format_result
from .queries import GQL_PROJECTS
from ...constants import NO_ACCESS_RIGHT


class QueriesProject:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def projects(self, project_id: str = None, search_query: str = None, skip: int = 0, first: int = 100):
        """
        Get projects with a search_query

        Parameters
        ----------
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
        variables = {
            'where': {
                'id': project_id,
                'searchQuery': search_query
            },
            'skip': skip,
            'first': first
        }
        result = self.auth.client.execute(GQL_PROJECTS, variables)
        return format_result('data', result)

    @deprecate(
        """
        This method is deprecated since: 30/04/2020.
        This method will be removed after: 30/05/2020.
        get_projects used to fetch projects. It is now achievable with projects. It will be removed on June 1st.
        To fetch projects, use:
            > playground.projects(search_query=search_query, skip=skip, first=first)
        """)
    def get_projects(self, user_id: str, search_query: str = None, skip: int = 0, first: int = 100):
        return self.projects(search_query=search_query, skip=skip, first=first)

    @deprecate(
        """
        This method is deprecated since: 30/04/2020.
        This method will be removed after: 30/05/2020.
        get_project used to fetch a project. It is now achievable with projects. It will be removed on June 1st.
        To fetch projects, use:
            > playground.projects(project_id=project_id)
        """)
    def get_project(self, project_id: str):
        projects = self.projects(project_id=project_id)
        assert len(projects) == 1, NO_ACCESS_RIGHT
        return projects[0]
