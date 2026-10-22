"""Organization domain."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, NewType, Optional

from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple

OrganizationId = NewType("OrganizationId", str)

OrganizationMetricName = Literal[
    "INTERACTIVE_SEGMENTATION",
    "LABELED_ASSETS",
    "LABELING_TIME",
    "NUMBER_OF_ANNOTATIONS",
    "REVIEW_TIME",
    "ROOT_NUMBER_OF_ANNOTATIONS",
    "VIDEO_TRACKING",
]

MetricsGranularity = Literal["HOUR", "DAY", "WEEK", "MONTH", "YEAR"]

# The metrics the Usage and license page totals on its usage card
USAGE_METRICS: tuple[OrganizationMetricName, ...] = (
    "LABELED_ASSETS",
    "NUMBER_OF_ANNOTATIONS",
    "ROOT_NUMBER_OF_ANNOTATIONS",
    "LABELING_TIME",
    "REVIEW_TIME",
)

# The metrics its usage-by-project table totals, whichever annotation count the licence uses
USAGE_BY_PROJECT_METRICS: tuple[OrganizationMetricName, ...] = (
    "LABELED_ASSETS",
    "NUMBER_OF_ANNOTATIONS",
    "ROOT_NUMBER_OF_ANNOTATIONS",
    "LABELING_TIME",
)


@dataclass(frozen=True)
class OrganizationFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    email: Optional[str] = None
    organization_id: Optional[OrganizationId] = None


@dataclass(frozen=True)
class OrganizationMetricsFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    id: OrganizationId
    start_datetime: datetime
    end_datetime: datetime


@dataclass(frozen=True)
class OrganizationUsageFilters:
    """Filters of the usage metrics of an organization, as the Usage and license page reads them."""

    metrics: ListOrTuple[OrganizationMetricName]
    organization_id: Optional[OrganizationId] = None
    project_id: Optional[ProjectId] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    granularity: Optional[MetricsGranularity] = None


@dataclass(frozen=True)
class OrganizationUsageByProjectFilters:
    """Filters of the usage metrics of an organization, totalled per project."""

    metrics: ListOrTuple[OrganizationMetricName]
    organization_id: Optional[OrganizationId] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    search_query: Optional[str] = None


@dataclass(frozen=True)
class OrganizationToCreateInput:
    """Organization to create use case input."""

    name: str


@dataclass(frozen=True)
class OrganizationToUpdateInput:
    """Organization to update use case input."""

    name: Optional[str] = None
    license: Optional[dict] = None
