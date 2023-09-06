"""Project use cases."""
from typing import Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.exceptions import NotFound


class ProjectUseCases:
    """Project use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self._kili_api_gateway = kili_api_gateway

    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: str,
        json_interface: dict,
        title: str,
        description: str,
        project_type: Optional[str],
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
