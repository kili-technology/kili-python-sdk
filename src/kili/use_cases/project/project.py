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
        title: str,
        description: str,
        project_type: Optional[ProjectType],
        compliance_tags: Optional[ListOrTuple[ComplianceTag]],
        project_id: Optional[ProjectId] = None,
        input_type: Optional[InputType] = None,
        json_interface: Optional[Dict] = None,
    ) -> ProjectId:
        """Create or copy a project if project_id is set."""
        if project_id is not None:
            project_copied = self._kili_api_gateway.get_project(
                project_id=project_id, fields=["jsonInterface", "instructions", "inputType"]
            )
            project_tag = self._kili_api_gateway.list_tags_by_project(
                project_id=project_id, fields=["id"]
            )
            new_project_id = self._kili_api_gateway.create_project(
                input_type=project_copied["inputType"],
                json_interface=project_copied["jsonInterface"],
                title=title,
                description=description,
                project_type=project_type,
                compliance_tags=compliance_tags,
            )
            if project_copied["instructions"]:
                self.update_properties_in_project(
                    project_id=new_project_id,
                    instructions=project_copied["instructions"],
                )
            tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id",))
            tags_of_orga_ids = [tag["id"] for tag in tags_of_orga]

            for tag in project_tag:
                if tag["id"] not in tags_of_orga_ids:
                    raise ValueError(
                        f"Tag {tag['id']} doesn't belong to your organization and was not copied."
                    )
                self._kili_api_gateway.check_tag(project_id=new_project_id, tag_id=tag["id"])
        elif input_type is None or json_interface is None:
            raise ValueError(
                """Arguments `input_type` and `json_interface` must be set
                if no `project_id` is providen."""
            )
        else:
            new_project_id = self._kili_api_gateway.create_project(
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
                _ = self._kili_api_gateway.get_project(project_id=new_project_id, fields=("id",))

        return ProjectId(new_project_id)

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
        can_navigate_between_assets: Optional[bool] = None,
        can_skip_asset: Optional[bool] = None,
        compliance_tags: Optional[ListOrTuple[ComplianceTag]] = None,
        consensus_mark: Optional[float] = None,
        consensus_tot_coverage: Optional[int] = None,
        description: Optional[str] = None,
        honeypot_mark: Optional[float] = None,
        instructions: Optional[str] = None,
        input_type: Optional[InputType] = None,
        json_interface: Optional[Dict] = None,
        min_consensus_size: Optional[int] = None,
        number_of_assets: Optional[int] = None,
        number_of_skipped_assets: Optional[int] = None,
        number_of_remaining_assets: Optional[int] = None,
        number_of_reviewed_assets: Optional[int] = None,
        review_coverage: Optional[int] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        title: Optional[str] = None,
        use_honeypot: Optional[bool] = None,
        metadata_types: Optional[Dict] = None,
        seconds_to_label_before_auto_assign: Optional[int] = None,
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
            seconds_to_label_before_auto_assign=seconds_to_label_before_auto_assign,
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
