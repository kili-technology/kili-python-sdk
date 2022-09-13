# pylint: disable=invalid-name,too-many-instance-attributes

"""
GraphQL types
"""

from dataclasses import dataclass


@dataclass
class License:
    """
    A Wrapper for License GraphQL object.
    """

    api = "api"
    apiPriority = "apiPriority"
    enableSmartTools = "enableSmartTools"
    expiryDate = "expiryDate"
    inputType = "inputType"
    maxNumberOfLabeledAssets = "maxNumberOfLabeledAssets"
    seats = "seats"
    startDate = "startDate"
    type = "type"
    uploadCloudData = "uploadCloudData"
    organizationId = "organizationId"


@dataclass
class OrganizationWithoutUser:
    """
    A wrapper for Organization GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    address = "address"
    canSeeDataset = "canSeeDataset"
    city = "city"
    country = "country"
    license = License
    name = "name"
    numberOfAnnotations = "numberOfAnnotations"
    numberOfLabeledAssets = "numberOfLabeledAssets"
    numberOfHours = "numberOfHours"
    zipCode = "zipCode"


@dataclass
class UserWithoutProjectUsers:
    """
    A wrapper for User GraphQL object.
    """

    id = "id"
    activated = "activated"
    createdAt = "createdAt"
    email = "email"
    firstname = "firstname"
    lastname = "lastname"
    organization = OrganizationWithoutUser
    organizationId = "organizationId"
    organizationIdCompute = "organizationIdCompute"
    organizationRole = "organizationRole"
    rights = "rights"
    updatedAt = "updatedAt"


@dataclass
class Organization(OrganizationWithoutUser):
    """
    A wrapper for Organization GraphQL object.
    """

    users = UserWithoutProjectUsers


@dataclass
class ProjectUserWithoutProject:
    """
    A wrapper for ProjectUser GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    activated = "activated"
    consensusMark = "consensusMark"
    consensusMarkPerCategory = "consensusMarkPerCategory"
    consensusMarkCompute = "consensusMarkCompute"
    honeypotMark = "honeypotMark"
    honeypotMarkCompute = "honeypotMarkCompute"
    lastLabelingAt = "lastLabelingAt"
    lastLabelingAtCompute = "lastLabelingAtCompute"
    numberOfAnnotations = "numberOfAnnotations"
    numberOfAnnotationsCompute = "numberOfAnnotationsCompute"
    numberOfLabeledAssets = "numberOfLabeledAssets"
    numberOfLabels = "numberOfLabels"
    numberOfLabelsCompute = "numberOfLabelsCompute"
    numberOfLabeledAssets = "numberOfLabeledAssets"
    numberOfLabeledAssetsCompute = "numberOfLabeledAssetsCompute"
    role = "role"
    starred = "starred"
    totalDuration = "totalDuration"
    totalDurationCompute = "totalDurationCompute"
    user = UserWithoutProjectUsers


@dataclass
class ProjectWithoutDataset:
    """
    A wrapper for Project GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    assetMetadata = "assetMetadata"
    assetMetadataCompute = "assetMetadataCompute"
    author = UserWithoutProjectUsers
    consensusMark = "consensusMark"
    consensusMarkPerCategory = "consensusMarkPerCategory"
    consensusTotCoverage = "consensusTotCoverage"
    createdAt = "createdAt"
    description = "description"
    honeypotMark = "honeypotMark"
    inputType = "inputType"
    instructions = "instructions"
    interface = "interface"
    interfaceCompute = "interfaceCompute"
    jsonInterface = "jsonInterface"
    minConsensusSize = "minConsensusSize"
    mlTasks = "mlTasks"
    mlTasksCompute = "mlTasksCompute"
    numberOfRemainingAssets = "numberOfRemainingAssets"
    numberOfAssets = "numberOfAssets"
    numberOfSkippedAssets = "numberOfSkippedAssets"
    numberOfOpenIssues = "numberOfOpenIssues"
    numberOfOpenQuestions = "numberOfOpenQuestions"
    numberOfSolvedIssues = "numberOfSolvedIssues"
    numberOfSolvedQuestions = "numberOfSolvedQuestions"
    numberOfReviewedAssets = "numberOfReviewedAssets"
    readPermissionsForAssetsAndLabels = "readPermissionsForAssetsAndLabels"
    reviewCoverage = "reviewCoverage"
    rights = "rights"
    roles = ProjectUserWithoutProject
    shouldRelaunchKpiComputation = "shouldRelaunchKpiComputation"
    title = "title"
    updatedAt = "updatedAt"
    useHoneyPot = "useHoneyPot"


@dataclass
class ProjectUser(ProjectUserWithoutProject):
    """
    A wrapper for ProjectUser GraphQL object.
    """

    project = ProjectWithoutDataset


@dataclass
class UserWithoutApiKey(UserWithoutProjectUsers):
    """
    A wrapper for User GraphQL object.
    """

    projectUsers = ProjectUser


@dataclass
class ApiKey:
    """
    A wrapper for ApiKey GraphQL object.
    """

    createdAt = "createdAt"
    id = "id"
    key = "key"
    name = "name"
    revoked = "revoked"
    user = UserWithoutApiKey
    userId = "userId"


@dataclass
class User(UserWithoutApiKey):
    """
    A wrapper for User GraphQL object.
    """

    apiKeys = ApiKey


@dataclass
class LabelWithoutLabelOf:
    """
    A wrapper for Label GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    assetIdCompute = "assetIdCompute"
    authorIdCompute = "authorIdCompute"
    author = User
    createdAt = "createdAt"
    honeypotMark = "honeypotMark"
    honeypotMarkCompute = "honeypotMarkCompute"
    inferenceMark = "inferenceMark"
    inferenceMarkCompute = "inferenceMarkCompute"
    isLatestLabelForUser = "isLatestLabelForUser"
    isLatestLabelForUserCompute = "isLatestLabelForUserCompute"
    isLatestDefaultLabelForUser = "isLatestDefaultLabelForUser"
    isLatestDefaultLabelForUserCompute = "isLatestDefaultLabelForUserCompute"
    isLatestReviewLabelForUser = "isLatestReviewLabelForUser"
    isLatestReviewLabelForUserCompute = "isLatestReviewLabelForUserCompute"
    jsonResponse = "jsonResponse"
    labelType = "labelType"
    modelName = "modelName"
    numberOfAnnotations = "numberOfAnnotations"
    numberOfAnnotationsCompute = "numberOfAnnotationsCompute"
    projectIdCompute = "projectIdCompute"
    responseCompute = "responseCompute"
    searchCompute = "searchCompute"
    secondsToLabel = "secondsToLabel"
    totalSecondsToLabel = "totalSecondsToLabel"
    totalSecondsToLabelCompute = "totalSecondsToLabelCompute"


@dataclass
class Lock:
    """
    A wrapper for Lock GraphQL object.
    """

    id = "id"
    author = User
    authorIdCompute = "authorIdCompute"
    createdAt = "createdAt"
    lockType = "lockType"
    lockOfIdCompute = "lockOfIdCompute"


@dataclass
class CommentsWithoutCommentsOf:
    """
    A wrapper for Comment GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    author = ProjectUser
    createdAt = "createdAt"
    text = "text"
    updatedAt = "updatedAt"


@dataclass
class CommentWithoutIssue:
    """
    A wrapper for Comment GraphQL object.
    """

    id = "id"
    author = ProjectUser
    authorId = "authorId"
    createdAt = "createdAt"
    issueId = "issueId"
    text = "text"
    updatedAt = "updatedAt"


@dataclass
class IssueWithoutAsset:
    """
    A wrapper for Issue GraphQL object.
    Defined in two steps to avoid cyclical dependencies.
    """

    id = "id"
    assetId = "assetId"
    assignee = ProjectUser
    assigneeId = "assigneeId"
    author = ProjectUser
    authorId = "authorId"
    comments = CommentWithoutIssue
    createdAt = "createdAt"
    hasBeenSeen = "hasBeenSeen"
    issueNumber = "issueNumber"
    objectMid = "objectMid"
    project: ProjectWithoutDataset
    projectId = "projectId"
    status = "status"
    type = "type"
    updatedAt = "updatedAt"


@dataclass
class Asset:
    """
    A wrapper for Asset GraphQL object.
    """

    id = "id"
    consensusMark = "consensusMark"
    consensusMarkCompute = "consensusMarkCompute"
    consensusMarkPerCategory = "consensusMarkPerCategory"
    content = "content"
    contentJson = "contentJson"
    contentJsonCompute = "contentJsonCompute"
    createdAt = "createdAt"
    duration = "duration"
    durationCompute = "durationCompute"
    externalId = "externalId"
    honeypotMark = "honeypotMark"
    honeypotMarkCompute = "honeypotMarkCompute"
    inferenceMark = "inferenceMark"
    inferenceMarkCompute = "inferenceMarkCompute"
    isHoneypot = "isHoneypot"
    isToBeLabeledBy = "isToBeLabeledBy"
    issues = IssueWithoutAsset
    isUsedForConsensus = "isUsedForConsensus"
    jsonContent = "jsonContent"
    jsonMetadata = "jsonMetadata"
    labels = LabelWithoutLabelOf
    latestLabel = LabelWithoutLabelOf
    latestLabelCompute = LabelWithoutLabelOf
    locks = Lock
    metadataCompute = "metadataCompute"
    metadata = "metadata"
    numberOfValidLocks = "numberOfValidLocks"
    numberOfValidLocksCompute = "numberOfValidLocksCompute"
    ocrMetadata = "ocrMetadata"
    priority = "priority"
    project = ProjectWithoutDataset
    projectId = "projectId"
    projectIdCompute = "projectIdCompute"
    readPermissionsFromLabels = "readPermissionsFromLabels"
    skipped = "skipped"
    status = "status"
    statusCompute = "statusCompute"
    thumbnail = "thumbnail"
    thumbnailCompute = "thumbnailCompute"
    toBeLabeledBy = ProjectUser
    updatedAt = "updatedAt"


@dataclass
class Label(LabelWithoutLabelOf):
    """
    A wrapper for Label GraphQL object.
    """

    labelOf = Asset


@dataclass
class Project(ProjectWithoutDataset):
    """
    A wrapper for Project GraphQL object.
    """

    dataset = Asset


@dataclass
class Notification:
    """
    A wrapper for Notification GraphQL object.
    """

    id = "id"
    createdAt = "createdAt"
    hasBeenSeen = "hasBeenSeen"
    message = "message"
    status = "status"
    url = "url"
    userID = "userID"


@dataclass
class ProjectVersion:
    """
    A wrapper for ProjectVersion GraphQL object.
    """

    id = "id"
    createdAt = "createdAt"
    content = "content"
    name = "name"
    project = Project
    projectId = "projectId"


@dataclass
class Issue(IssueWithoutAsset):
    """
    A wrapper for Issue GraphQL object.
    """

    asset: Asset


@dataclass
class Comment(CommentWithoutIssue):
    """
    A wrapper for Comment GraphQL object.
    """

    issue = Issue


# pylint: enable=invalid-name
