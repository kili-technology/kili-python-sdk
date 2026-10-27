"""Organization client methods."""

from collections.abc import Generator, Iterable
from datetime import datetime, timezone
from typing import Literal, Optional, overload

from typeguard import typechecked
from typing_extensions import deprecated

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.organization import (
    USAGE_BY_PROJECT_METRICS,
    USAGE_METRICS,
    MetricsGranularity,
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricName,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
    OrganizationUsageByProjectFilters,
    OrganizationUsageFilters,
)
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.presentation.client.base import BaseClientMethods
from kili.presentation.client.helpers.common_validators import resolve_disable_tqdm
from kili.use_cases.organization.use_cases import OrganizationUseCases
from kili.utils.logcontext import for_all_methods, log_call

ORGANIZATION_METRICS_DEPRECATION = (
    "organization_metrics is deprecated and will be removed: use organization_usage() instead,"
    " which counts as the Usage and license page of the app does."
)


@for_all_methods(log_call, exclude=["__init__"])
class InternalOrganizationClientMethods(BaseClientMethods):
    """Organization client methods."""

    @typechecked
    def create_organization(
        self,
        name: str,
    ) -> dict:
        """Create an organization.

        WARNING: This method is for internal use only.

        Each user must be linked to an organization

        Args:
            name : Name of the organization

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        organization_use_case = OrganizationUseCases(self.kili_api_gateway)
        return organization_use_case.create_organization(
            OrganizationToCreateInput(
                name=name,
            ),
        )

    @typechecked
    def update_properties_in_organization(
        self,
        organization_id: str,
        name: Optional[str] = None,
        license: Optional[dict] = None,  # noqa: A002
    ) -> dict:
        """Modify an organization.

        WARNING: This method is for internal use only.

        Args:
            organization_id: Identifier of the organization
            name: New name of the organization
            license: New license of the organization

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        use_cases = OrganizationUseCases(self.kili_api_gateway)
        return use_cases.update_organization(
            OrganizationId(organization_id),
            OrganizationToUpdateInput(name=name, license=license),
        )


@for_all_methods(log_call, exclude=["__init__"])
class OrganizationClientMethods(BaseClientMethods):
    """Organization client methods."""

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[dict, None, None]:
        ...

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> list[dict]:
        ...

    @typechecked
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/organization) for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the organizations is returned.

        Returns:
            An iterable of organizations.

        Examples:
            >>> kili.organizations(organization_id=organization_id, fields=['users.email'])
            [{'users': [{'email': 'john@doe.com'}]}]
        """
        disable_tqdm = resolve_disable_tqdm(disable_tqdm, getattr(self, "disable_tqdm", None))
        organization_use_cases = OrganizationUseCases(self.kili_api_gateway)
        organization_gen = organization_use_cases.list_organizations(
            OrganizationFilters(
                email=email,
                organization_id=OrganizationId(organization_id) if organization_id else None,
            ),
            fields,
            QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip),
        )

        if as_generator:
            return organization_gen
        return list(organization_gen)

    @typechecked
    def count_organizations(
        self, email: Optional[str] = None, organization_id: Optional[str] = None
    ) -> int:
        """Count organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization

        Returns:
            An integer corresponding to the number of organizations that match the criteria.
        """
        where = OrganizationFilters(
            email=email,
            organization_id=OrganizationId(organization_id) if organization_id else None,
        )
        return OrganizationUseCases(self.kili_api_gateway).count_organizations(where)

    @typechecked
    def organization_usage(
        self,
        metrics: ListOrTuple[OrganizationMetricName] = USAGE_METRICS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: Optional[MetricsGranularity] = None,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> list[dict]:
        """Get the usage metrics of your organization, as the Usage and license page shows them.

        Only organization admins can call it.

        Args:
            metrics: The metrics to return. Times (`LABELING_TIME`, `REVIEW_TIME`) are in seconds.
                The page counts annotations with `ROOT_NUMBER_OF_ANNOTATIONS` when your licence
                counts root annotations only, and with `NUMBER_OF_ANNOTATIONS` otherwise.
            start_date: Start of the period, floored to its day in UTC. Defaults to the start of
                your licence. A naive datetime is read as UTC.
            end_date: End of the period. Defaults to now. Usage is kept per UTC day: the day
                `end_date` falls in counts in full, unless `end_date` is its midnight. A naive
                datetime is read as UTC.
            granularity: Size of the buckets of `details`: `DAY`, `WEEK`, `MONTH` or `YEAR` (the
                default); `HOUR` gives days too. The page uses `DAY` for a month and `MONTH` for a
                year.
            project_id: Restrict the metrics to this project.
            organization_id: Identifier of the organization, yours by default. Only Kili admins
                can name another, and the default start date still follows your own licence.

        Returns:
            One dictionary per metric with usage over the period: `metric`, its `total`, and its
                `details`, one `{"timestamp", "value"}` per bucket and per project. A metric with
                no usage is absent: read it as 0.

        Examples:
            >>> from datetime import datetime
            >>> kili.organization_usage(
            ...     metrics=["LABELED_ASSETS", "LABELING_TIME"],
            ...     start_date=datetime(2026, 10, 1),
            ...     end_date=datetime(2026, 11, 1),
            ...     granularity="DAY",
            ... )
            [{'metric': 'LABELED_ASSETS', 'total': 120, 'details': [...]},
             {'metric': 'LABELING_TIME', 'total': 45000, 'details': [...]}]
        """
        filters = OrganizationUsageFilters(
            metrics=metrics,
            organization_id=OrganizationId(organization_id) if organization_id else None,
            project_id=ProjectId(project_id) if project_id else None,
            start_datetime=start_date,
            end_datetime=end_date,
            granularity=granularity,
        )
        return OrganizationUseCases(self.kili_api_gateway).get_organization_usage(filters)

    @overload
    def organization_usage_by_project(
        self,
        metrics: ListOrTuple[OrganizationMetricName] = USAGE_BY_PROJECT_METRICS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        organization_id: Optional[str] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[dict, None, None]:
        ...

    @overload
    def organization_usage_by_project(
        self,
        metrics: ListOrTuple[OrganizationMetricName] = USAGE_BY_PROJECT_METRICS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        organization_id: Optional[str] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> list[dict]:
        ...

    @typechecked
    def organization_usage_by_project(
        self,
        metrics: ListOrTuple[OrganizationMetricName] = USAGE_BY_PROJECT_METRICS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        organization_id: Optional[str] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[dict]:
        """Get the usage metrics per project, as the Usage and license page lists them.

        Only organization admins can call it. Projects come busiest first, ranked by the annotation
        metric your licence counts, which is added to the metrics asked for; a project with no usage
        of these metrics over the period is not listed. Every page ranks the whole organization
        again: on a large one, set `first` or narrow the period.

        Args:
            metrics: The metrics to total per project. Times (`LABELING_TIME`, `REVIEW_TIME`) are in
                seconds.
            start_date: Start of the period, floored to its day in UTC. Defaults to the start of
                your licence. A naive datetime is read as UTC.
            end_date: End of the period. Defaults to now. Usage is kept per UTC day: the day
                `end_date` falls in counts in full, unless `end_date` is its midnight. A naive
                datetime is read as UTC.
            search_query: Case-insensitive filter on the project title, description or id.
            organization_id: Identifier of the organization, yours by default. Only Kili admins
                can name another, and the default start date and the ranking still follow your own
                licence.
            first: Maximum number of projects to return.
            skip: Number of projects to skip, in rank order.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the projects is returned.

        Returns:
            An iterable of projects: `projectId`, `projectTitle`, `isDeleted`, and `metrics`, one
                `{"metric", "total"}` per metric the project has usage for: a missing one is 0.

        Examples:
            >>> kili.organization_usage_by_project(metrics=["LABELED_ASSETS"], first=2)
            [{'projectId': 'clx…', 'projectTitle': 'Retail shelves', 'isDeleted': False,
              'metrics': [{'metric': 'LABELED_ASSETS', 'total': 120}]}, ...]
        """
        disable_tqdm = resolve_disable_tqdm(disable_tqdm, getattr(self, "disable_tqdm", None))
        projects = OrganizationUseCases(self.kili_api_gateway).list_organization_usage_by_project(
            OrganizationUsageByProjectFilters(
                metrics=metrics,
                organization_id=OrganizationId(organization_id) if organization_id else None,
                start_datetime=start_date,
                end_datetime=end_date,
                search_query=search_query,
            ),
            QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip),
        )
        if as_generator:
            return projects
        return list(projects)

    @deprecated(ORGANIZATION_METRICS_DEPRECATION)
    @typechecked
    def organization_metrics(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        fields: ListOrTuple[str] = (
            "numberOfAnnotations",
            "numberOfHours",
            "numberOfLabeledAssets",
        ),
    ) -> dict:
        """Get organization metrics.

        !!! warning "Deprecated"
            This method will be removed: use `organization_usage()` instead, which counts as the
            Usage and license page of the app does. Only organization admins can call it.

        Args:
            organization_id: Identifier of the organization
            start_date: Start date of the metrics computation
            end_date: End date of the metrics computation
            fields: Fields to request for the organization metrics.

        Returns:
            A dictionary containing the metrics of the organization.
        """
        if start_date is None:
            start_date = datetime.now(tz=timezone.utc)
        if end_date is None:
            end_date = datetime.now(tz=timezone.utc)
        filters = OrganizationMetricsFilters(
            id=OrganizationId(organization_id), start_datetime=start_date, end_datetime=end_date
        )

        return OrganizationUseCases(self.kili_api_gateway).get_organization_metrics(filters, fields)
