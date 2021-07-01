class OrganizationWithoutUser(object):
    id = 'id'
    address = 'address'
    city = 'city'
    country = 'country'
    license = 'license'
    name = 'name'
    numberOfAnnotations = 'numberOfAnnotations'
    numberOfLabeledAssets = 'numberOfLabeledAssets'
    numberOfHours = 'numberOfHours'
    zipCode = 'zipCode'


class UserWithoutProjectUsers(object):
    id = 'id'
    activated = 'activated'
    createdAt = 'createdAt'
    email = 'email'
    name = 'name'
    organization = OrganizationWithoutUser
    organizationId = 'organizationId'
    organizationIdCompute = 'organizationIdCompute'
    organizationRole = 'organizationRole'
    rights = 'rights'
    updatedAt = 'updatedAt'


class Organization(OrganizationWithoutUser):
    users = UserWithoutProjectUsers


class ProjectUserWithoutProject(object):
    id = 'id'
    activated = 'activated'
    consensusMark = 'consensusMark'
    consensusMarkPerCategory = 'consensusMarkPerCategory'
    consensusMarkCompute = 'consensusMarkCompute'
    honeypotMark = "honeypotMark"
    honeypotMarkCompute = 'honeypotMarkCompute'
    lastLabelingAt = "lastLabelingAt"
    lastLabelingAtCompute = 'lastLabelingAtCompute'
    numberOfAnnotations = "numberOfAnnotations"
    numberOfAnnotationsCompute = 'numberOfAnnotationsCompute'
    numberOfLabeledAssets = "numberOfLabeledAssets"
    numberOfLabels = "numberOfLabels"
    numberOfLabelsCompute = 'numberOfLabelsCompute'
    numberOfLabeledAssets = 'numberOfLabeledAssets'
    numberOfLabeledAssetsCompute = 'numberOfLabeledAssetsCompute'
    role = 'role'
    starred = 'starred'
    totalDuration = "totalDuration"
    totalDurationCompute = 'totalDurationCompute'
    user = UserWithoutProjectUsers


class ProjectWithoutDataset(object):
    id = 'id'
    assetMetadata = 'assetMetadata'
    assetMetadataCompute = 'assetMetadataCompute'
    author = UserWithoutProjectUsers
    consensusMark = 'consensusMark'
    consensusMarkPerCategory = 'consensusMarkPerCategory'
    consensusTotCoverage = 'consensusTotCoverage'
    createdAt = 'createdAt'
    description = 'description'
    honeypotMark = 'honeypotMark'
    inputType = 'inputType'
    instructions = 'instructions'
    interface = 'interface'
    interfaceCategory = 'interfaceCategory'
    interfaceCompute = 'interfaceCompute'
    jsonInterface = 'jsonInterface'
    maxWorkerCount = 'maxWorkerCount'
    minAgreement = 'minAgreement'
    minConsensusSize = 'minConsensusSize'
    numberOfRemainingAssets = 'numberOfRemainingAssets'
    numberOfAssets = 'numberOfAssets'
    numberOfAssetsWithSkippedLabels = 'numberOfAssetsWithSkippedLabels'
    numberOfOpenIssues = 'numberOfOpenIssues'
    numberOfSolvedIssues = 'numberOfSolvedIssues'
    numberOfReviewedAssets = 'numberOfReviewedAssets'
    readPermissionsForAssetsAndLabels = 'readPermissionsForAssetsAndLabels'
    reviewCoverage = 'reviewCoverage'
    rights = 'rights'
    roles = ProjectUserWithoutProject
    shouldRelaunchKpiComputation = 'shouldRelaunchKpiComputation'
    title = 'title'
    titleAndDescription = 'titleAndDescription'
    updatedAt = 'updatedAt'
    useHoneyPot = 'useHoneyPot'


class ProjectUser(ProjectUserWithoutProject):
    project = ProjectWithoutDataset


class User(UserWithoutProjectUsers):
    projectUsers = ProjectUser


class LabelWithoutLabelOf(object):
    id = 'id'
    assetIdCompute = 'assetIdCompute'
    authorIdCompute = 'authorIdCompute'
    author = User
    createdAt = 'createdAt'
    honeypotMark = 'honeypotMark'
    honeypotMarkCompute = 'honeypotMarkCompute'
    inferenceMark = 'inferenceMark'
    inferenceMarkCompute = 'inferenceMarkCompute'
    isLatestLabelForUser = 'isLatestLabelForUser'
    isLatestLabelForUserCompute = 'isLatestLabelForUserCompute'
    isLatestDefaultLabelForUser = 'isLatestDefaultLabelForUser'
    isLatestDefaultLabelForUserCompute = 'isLatestDefaultLabelForUserCompute'
    jsonResponse = 'jsonResponse'
    labelType = 'labelType'
    modelName = 'modelName'
    numberOfAnnotations = 'numberOfAnnotations'
    numberOfAnnotationsCompute = 'numberOfAnnotationsCompute'
    projectIdCompute = 'projectIdCompute'
    responseCompute = 'responseCompute'
    searchCompute = 'searchCompute'
    secondsToLabel = 'secondsToLabel'
    skipped = 'skipped'
    totalSecondsToLabel = 'totalSecondsToLabel'
    totalSecondsToLabelCompute = 'totalSecondsToLabelCompute'


class Lock(object):
    id = 'id'
    author = User
    authorIdCompute = 'authorIdCompute'
    createdAt = 'createdAt'
    lockType = 'lockType'
    lockOfIdCompute = 'lockOfIdCompute'


class CommentsWithoutCommentsOf(object):
    id = 'id'
    author = ProjectUser
    createdAt = 'createdAt'
    text = 'text'
    updatedAt = 'updatedAt'


class Issue(object):
    id = 'id'
    assignee = ProjectUser
    author = ProjectUser
    comments = CommentsWithoutCommentsOf
    createdAt = 'createdAt'
    hasBeenSeen = 'hasBeenSeen'
    issueNumber = 'issueNumber'
    project = ProjectWithoutDataset
    status = 'status'
    type = 'type'
    updatedAt = 'updatedAt'


class Asset(object):
    id = 'id'
    consensusMark = 'consensusMark'
    consensusMarkCompute = 'consensusMarkCompute'
    consensusMarkPerCategory = 'consensusMarkPerCategory'
    content = 'content'
    contentJson = 'contentJson'
    contentJsonCompute = 'contentJsonCompute'
    createdAt = 'createdAt'
    duration = 'duration'
    durationCompute = 'durationCompute'
    externalId = 'externalId'
    honeypotMark = 'honeypotMark'
    honeypotMarkCompute = 'honeypotMarkCompute'
    inferenceMark = 'inferenceMark'
    inferenceMarkCompute = 'inferenceMarkCompute'
    isHoneypot = 'isHoneypot'
    isToBeLabeledBy = 'isToBeLabeledBy'
    issues = Issue
    isUsedForConsensus = 'isUsedForConsensus'
    jsonContent = 'jsonContent'
    jsonMetadata = 'jsonMetadata'
    labels = LabelWithoutLabelOf
    locks = Lock
    metadataCompute = 'metadataCompute'
    metadata = 'metadata'
    numberOfValidLocks = 'numberOfValidLocks'
    numberOfValidLocksCompute = 'numberOfValidLocksCompute'
    priority = 'priority'
    project = ProjectWithoutDataset
    projectIdCompute = 'projectIdCompute'
    readPermissionsFromLabels = 'readPermissionsFromLabels'
    status = 'status'
    statusCompute = 'statusCompute'
    thumbnail = 'thumbnail'
    thumbnailCompute = 'thumbnailCompute'
    toBeLabeledBy = ProjectUser
    updatedAt = 'updatedAt'


class DatasetAsset(object):
    id = 'id'
    content = 'content'
    contentJson = 'contentJson'
    contentJsonCompute = 'contentJsonCompute'
    createdAt = 'createdAt'
    externalId = 'externalId'
    jsonContent = 'jsonContent'
    jsonMetadata = 'jsonMetadata'
    metadataCompute = 'metadataCompute'
    metadata = 'metadata'
    thumbnail = 'thumbnail'
    thumbnailCompute = 'thumbnailCompute'
    updatedAt = 'updatedAt'


class Label(LabelWithoutLabelOf):
    labelOf = Asset


class Project(ProjectWithoutDataset):
    dataset = Asset


class Notification(object):
    id = 'id'
    createdAt = 'createdAt'
    hasBeenSeen = 'hasBeenSeen'
    message = 'message'
    status = 'status'
    url = 'url'
    userID = 'userID'


class ProjectVersion(object):
    id = 'id'
    createdAt = 'createdAt'
    content = 'content'
    name = 'name'
    project = Project
    projectId = 'projectId'
