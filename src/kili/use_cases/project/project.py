"""Project use cases."""

import json
from typing import Dict, Generator, Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.project.mappers import project_data_mapper
from kili.adapters.kili_api_gateway.project.types import ProjectDataKiliAPIGatewayInput
from kili.core.enums import ProjectType
from kili.domain.project import ComplianceTag, InputType, ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound
from kili.use_cases.base import BaseUseCases


class ProjectUseCases(BaseUseCases):
    """Project use cases."""

    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: InputType,
        json_interface: Dict,
        title: str,
        description: str,
        project_type: Optional[ProjectType],
        compliance_tags: Optional[ListOrTuple[ComplianceTag]],
    ) -> ProjectId:
        """Create a project."""
        project_id = self._kili_api_gateway.create_project(
            input_type=input_type,
            json_interface=json_interface,
            title=title,
            description=description,
            project_type=project_type,
            compliance_tags=compliance_tags,
        )

        # The project is not immediately available after creation
        for attempt in Retrying(
            stop=stop_after_delay(60),
            wait=wait_fixed(1),
            retry=retry_if_exception_type(NotFound),
            reraise=True,
        ):
            with attempt:
                _ = self._kili_api_gateway.get_project(project_id=project_id, fields=("id",))

        return ProjectId(project_id)

    def list_projects(
        self,
        project_filters: ProjectFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """Return a generator of projects that match the filter."""
        return self._kili_api_gateway.list_projects(project_filters, fields, options=options)

    def count_projects(self, project_filters: ProjectFilters) -> int:
        """Return the number of projects that match the filter."""
        return self._kili_api_gateway.count_projects(project_filters)

    # pylint: disable=too-many-locals
    def update_properties_in_project(
        self,
        project_id: ProjectId,
        *,
        can_navigate_between_assets: Optional[bool],
        can_skip_asset: Optional[bool],
        compliance_tags: Optional[ListOrTuple[ComplianceTag]],
        consensus_mark: Optional[float],
        consensus_tot_coverage: Optional[int],
        description: Optional[str],
        honeypot_mark: Optional[float],
        instructions: Optional[str],
        input_type: Optional[InputType],
        json_interface: Optional[Dict],
        min_consensus_size: Optional[int],
        number_of_assets: Optional[int],
        number_of_skipped_assets: Optional[int],
        number_of_remaining_assets: Optional[int],
        number_of_reviewed_assets: Optional[int],
        review_coverage: Optional[int],
        should_relaunch_kpi_computation: Optional[bool],
        title: Optional[str],
        use_honeypot: Optional[bool],
        metadata_types: Optional[Dict],
    ) -> Dict[str, object]:
        """Update properties in a project."""
        if consensus_tot_coverage is not None and not 0 <= consensus_tot_coverage <= 100:
            raise ValueError(
                "Argument `consensus_tot_coverage` must be comprised between 0 and 100."
            )

        if min_consensus_size is not None and not 1 <= min_consensus_size <= 10:
            raise ValueError("Argument `min_consensus_size` must be comprised between 1 and 10.")

        if review_coverage is not None and not 0 <= review_coverage <= 100:
            raise ValueError("Argument `review_coverage` must be comprised between 0 and 100.")

        project_data = ProjectDataKiliAPIGatewayInput(
            can_navigate_between_assets=can_navigate_between_assets,
            can_skip_asset=can_skip_asset,
            consensus_mark=consensus_mark,
            consensus_tot_coverage=consensus_tot_coverage,
            compliance_tags=compliance_tags,
            description=description,
            honeypot_mark=honeypot_mark,
            instructions=instructions,
            input_type=input_type,
            json_interface=json.dumps(json_interface) if json_interface is not None else None,
            metadata_types=metadata_types,
            min_consensus_size=min_consensus_size,
            number_of_assets=number_of_assets,
            number_of_skipped_assets=number_of_skipped_assets,
            number_of_remaining_assets=number_of_remaining_assets,
            number_of_reviewed_assets=number_of_reviewed_assets,
            review_coverage=review_coverage,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            title=title,
            use_honeypot=use_honeypot,
            archived=None,
            author=None,
            rules=None,
        )

        fields = tuple(
            name for name, val in project_data_mapper(project_data).items() if val is not None
        )
        if "id" not in fields:
            fields += ("id",)

        return self._kili_api_gateway.update_properties_in_project(project_id, project_data, fields)
