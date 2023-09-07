"""Project use cases."""
from typing import Dict, Generator, Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.enums import ProjectType
from kili.domain.project import InputType, ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound


class ProjectUseCases:
    """Project use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self._kili_api_gateway = kili_api_gateway

    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: InputType,
        json_interface: Dict,
        title: str,
        description: str,
        project_type: Optional[ProjectType],
    ) -> ProjectId:
        """Create a project."""
        project_id = self._kili_api_gateway.create_project(
            input_type=input_type,
            json_interface=json_interface,
            title=title,
            description=description,
            project_type=project_type,
        )

        # The project is not immediately available after creation
        for attempt in Retrying(
            stop=stop_after_delay(60),
            wait=wait_fixed(1),
            retry=retry_if_exception_type(NotFound),
            reraise=True,
        ):
            with attempt:
                _ = self._kili_api_gateway.get_project(project_id=project_id, fields=["id"])

        return ProjectId(project_id)

    def list_projects(
        self,
        project_filters: ProjectFilters,
        fields: ListOrTuple[str],
        first: Optional[int],
        skip: int,
        disable_tqdm: Optional[bool],
    ) -> Generator[Dict, None, None]:
        """Return a generator of projects that match the filter."""
        return self._kili_api_gateway.list_projects(
            project_filters,
            fields,
            options=QueryOptions(skip=skip, first=first, disable_tqdm=disable_tqdm),
        )
