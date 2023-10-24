# pylint: disable:invalid-name,too-many-instance-attributes
"""GraphQL types."""
from typing import Dict, List

from typing_extensions import TypedDict

from kili.core.enums import (
    LicenseType,
    LockType,
    NotificationStatus,
    OrganizationRole,
    ProjectRole,
    Right,
)
from kili.core.helpers import deprecate
from kili.domain.asset import AssetStatus
from kili.domain.issue import IssueStatus
from kili.domain.label import LabelType
from kili.domain.project import InputType


#######
# The following types are deprecated and will be removed in the next major release.
@deprecate()
class License(TypedDict):
    """A Wrapper for License GraphQL object."""

    api: bool
    apiPriority: bool
    canUsePlugins: bool
    enableSmartTools: bool
    expiryDate: str
    inputType: InputType
    maxNumberOfAnnotations: int
    maxNumberOfAnnotationsPerMonth: int
    maxNumberOfLabeledAssets: int
    maxNumberOfPredictionsPerMonth: int
    organizationId: int
    seats: int
    startDate: str
    type: LicenseType
    uploadCloudData: bool
    uploadLocalData: bool


@deprecate()
class OrganizationWithoutUser(TypedDict):
    """A wrapper for Organization GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    address: str
    canSeeDataset: bool
    city: str
    country: str
    license: License
    name: str
    numberOfAnnotations: int
    numberOfLabeledAssets: int
    numberOfHours: float
    zipCode: str


@deprecate()
class UserWithoutProjectUsers(TypedDict):
    """A wrapper for User GraphQL object."""

    id: str
    activated: bool
    createdAt: str
    email: str
    firstname: str
    lastname: str
    organization: OrganizationWithoutUser
    organizationId: str
    organizationRole: OrganizationRole
    rights: Right
    updatedAt: str


@deprecate()
class Organization(OrganizationWithoutUser):
    """A wrapper for Organization GraphQL object."""

    users: UserWithoutProjectUsers


@deprecate()
class ProjectUserWithoutProject(TypedDict):
    """A wrapper for ProjectUser GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    activated: bool
    consensusMark: float
    consensusMarkPerCategory: Dict
    consensusMarkCompute: float
    honeypotMark: float
    honeypotMarkCompute: float
    lastLabelingAt: str
    lastLabelingAtCompute: str
    numberOfAnnotations: int
    numberOfAnnotationsCompute: int
    numberOfLabeledAssets: int
    numberOfLabels: int
    numberOfLabelsCompute: int
    numberOfLabeledAssetsCompute: int
    role: ProjectRole
    starred: bool
    totalDuration: float
    totalDurationCompute: float
    user: UserWithoutProjectUsers


@deprecate()
class DataConnection(TypedDict):
    """A wrapper for DataConnection GraphQL object."""

    id: str
    isChecking: bool
    isApplyingDataDifferences: bool
    numberOfAssets: int
    projectId: str
    dataIntegrationId: str


@deprecate()
class ProjectWithoutDataset(TypedDict, total=False):
    """A wrapper for Project GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    assetMetadata: Dict
    assetMetadataCompute: Dict
    author: UserWithoutProjectUsers
    canNavigateBetweenAssets: bool
    canSkipAsset: bool
    consensusMark: float
    consensusMarkPerCategory: Dict
    consensusTotCoverage: int
    createdAt: str
    dataConnections: DataConnection
    description: str
    honeypotMark: float
    inputType: InputType
    instructions: str
    interface: Dict
    interfaceCompute: Dict
    jsonInterface: Dict
    metadataTypes: Dict
    minConsensusSize: int
    mlTasks: str
    mlTasksCompute: str
    numberOfRemainingAssets: int
    numberOfAssets: int
    numberOfSkippedAssets: int
    numberOfOpenIssues: int
    numberOfOpenQuestions: int
    numberOfSolvedIssues: int
    numberOfSolvedQuestions: int
    numberOfReviewedAssets: int
    readPermissionsForAssetsAndLabels: str
    reviewCoverage: int
    rights: Right
    roles: ProjectUserWithoutProject
    shouldRelaunchKpiComputation: bool
    title: str
    updatedAt: str
    useHoneyPot: bool


@deprecate()
class ProjectUser(ProjectUserWithoutProject):
    """A wrapper for ProjectUser GraphQL object."""

    project: ProjectWithoutDataset


@deprecate()
class UserWithoutApiKey(UserWithoutProjectUsers):
    """A wrapper for User GraphQL object."""

    projectUsers: ProjectUser


@deprecate()
class ApiKey(TypedDict):
    """A wrapper for ApiKey GraphQL object."""

    createdAt: str
    id: str
    key: str
    name: str
    revoked: bool
    user: UserWithoutApiKey  # ? Why not just User
    userId: str


@deprecate()
class User(UserWithoutApiKey):
    """A wrapper for User GraphQL object."""

    apiKeys: ApiKey


@deprecate()
class LabelWithoutLabelOf(TypedDict):
    """A wrapper for Label GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    assetIdCompute: str
    authorIdCompute: str
    author: User
    createdAt: str
    honeypotMark: float
    honeypotMarkCompute: float
    inferenceMark: float
    inferenceMarkCompute: float
    isLatestLabelForUser: bool
    isLatestLabelForUserCompute: bool
    isLatestDefaultLabelForUser: bool
    isLatestDefaultLabelForUserCompute: bool
    isLatestReviewLabelForUser: bool
    isLatestReviewLabelForUserCompute: bool
    jsonResponse: Dict
    labelType: LabelType
    modelName: str
    numberOfAnnotations: int
    numberOfAnnotationsCompute: int
    projectIdCompute: str
    responseCompute: Dict
    searchCompute: Dict
    secondsToLabel: int
    totalSecondsToLabel: float
    totalSecondsToLabelCompute: float


@deprecate()
class Lock(TypedDict):
    """A wrapper for Lock GraphQL object."""

    id: str
    author: User
    authorIdCompute: str
    createdAt: str
    lockType: LockType
    lockOfIdCompute: str


@deprecate()
class CommentsWithoutCommentsOf(TypedDict):
    """A wrapper for Comment GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    author: ProjectUser
    createdAt: str
    text: str
    updatedAt: str


@deprecate()
class CommentWithoutIssue(TypedDict):
    """A wrapper for Comment GraphQL object."""

    id: str
    author: ProjectUser
    authorId: str
    createdAt: str
    issueId: str
    text: str
    updatedAt: str


@deprecate()
class IssueWithoutAsset(TypedDict):
    """A wrapper for Issue GraphQL object.

    Defined in two steps to avoid cyclical dependencies.
    """

    id: str
    assetId: str
    assignee: ProjectUser
    assigneeId: str
    author: ProjectUser
    authorId: str
    comments: CommentWithoutIssue
    createdAt: str
    hasBeenSeen: bool
    issueNumber: int
    objectMid: str
    project: ProjectWithoutDataset
    projectId: str
    status: IssueStatus
    type: "type"
    updatedAt: str


@deprecate()
class Asset(TypedDict):
    """A wrapper for Asset GraphQL object."""

    id: str
    consensusMark: float
    consensusMarkCompute: float
    consensusMarkPerCategory: Dict
    content: str
    contentJson: Dict
    contentJsonCompute: Dict
    createdAt: str
    duration: float
    durationCompute: float
    externalId: str
    honeypotMark: float
    honeypotMarkCompute: float
    inferenceMark: float
    inferenceMarkCompute: float
    isHoneypot: bool
    isToBeLabeledBy: bool
    issues: IssueWithoutAsset
    isUsedForConsensus: bool
    jsonContent: Dict
    jsonMetadata: Dict
    labels: LabelWithoutLabelOf
    latestLabel: LabelWithoutLabelOf
    latestLabelCompute: LabelWithoutLabelOf
    locks: Lock
    metadataCompute: Dict
    metadata: Dict
    numberOfValidLocks: int
    numberOfValidLocksCompute: int
    ocrMetadata: Dict
    priority: int
    project: ProjectWithoutDataset
    projectId: str
    projectIdCompute: str
    readPermissionsFromLabels: str
    skipped: bool
    status: AssetStatus
    statusCompute: AssetStatus
    thumbnail: str
    thumbnailCompute: str
    toBeLabeledBy: ProjectUser
    updatedAt: str


@deprecate()
class Label(LabelWithoutLabelOf):
    """A wrapper for Label GraphQL object."""

    labelOf: Asset


@deprecate()
class Project(ProjectWithoutDataset, total=False):
    """A wrapper for Project GraphQL object."""

    dataset: Asset


@deprecate()
class Notification(TypedDict):
    """A wrapper for Notification GraphQL object."""

    id: str
    createdAt: str
    hasBeenSeen: bool
    message: str
    status: NotificationStatus
    url: str
    userID: str


@deprecate()
class Plugin(TypedDict):
    """A wrapper for Plugin GraphQL object."""

    id: str
    name: str
    projectIds: List[str]
    createdAt: str
    updatedAt: str


@deprecate()
class ProjectVersion(TypedDict):
    """A wrapper for ProjectVersion GraphQL object."""

    id: str
    createdAt: str
    content: str
    name: str
    project: Project
    projectId: str


@deprecate()
class Issue(IssueWithoutAsset):
    """A wrapper for Issue GraphQL object."""

    asset: Asset


@deprecate()
class Comment(CommentWithoutIssue):
    """A wrapper for Comment GraphQL object."""

    issue: Issue


# pylint: enable:invalid-name
