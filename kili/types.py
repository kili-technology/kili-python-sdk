class Organization(object):
    id = 'id'
    address = 'address'
    city = 'city'
    country = 'country'
    name = 'name'
    zipCode = 'zipCode'


class UserWithoutProjectUsers(object):
    id = 'id'
    activated = 'activated'
    createdAt = 'createdAt'
    email = 'email'
    name = 'name'
    organization = Organization
    organizationId = 'organizationId'
    organizationIdCompute = 'organizationIdCompute'
    organizationRole = 'organizationRole'
    updatedAt = 'updatedAt'


class ProjectUserWithoutProject(object):
    id = 'id'
    activated = 'activated'
    consensusMark = 'consensusMark'
    honeypotMark = "honeypotMark"
    lastLabelingAt = "lastLabelingAt"
    numberOfAnnotations = "numberOfAnnotations"
    numberOfLabeledAssets = "numberOfLabeledAssets"
    numberOfLabels = "numberOfLabels"
    role = 'role'
    starred = 'starred'
    totalDuration = "totalDuration"
    user = UserWithoutProjectUsers


class ProjectWithoutDataset(object):
    id = 'id'
    author = UserWithoutProjectUsers
    consensusMark = 'consensusMark'
    consensusTotCoverage = 'consensusTotCoverage'
    createdAt = 'createdAt'
    description = 'description'
    honeypotMark = 'honeypotMark'
    inputType = 'inputType'
    instructions = 'instructions'
    interfaceCategory = 'interfaceCategory'
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


class Asset(object):
    id = 'id'
    consensusMark = 'consensusMark'
    consensusMarkCompute = 'consensusMarkCompute'
    content = 'content'
    createdAt = 'createdAt'
    duration = 'duration'
    durationCompute = 'durationCompute'
    externalId = 'externalId'
    honeypotMark = 'honeypotMark'
    honeypotMarkCompute = 'honeypotMarkCompute'
    isHoneypot = 'isHoneypot'
    isToBeLabeledByCompute = 'isToBeLabeledByCompute'
    isUsedForConsensus = 'isUsedForConsensus'
    jsonContent = 'jsonContent'
    jsonMetadata = 'jsonMetadata'
    labels = LabelWithoutLabelOf
    locks = Lock
    numberOfValidLocks = 'numberOfValidLocks'
    numberOfValidLocksCompute = 'numberOfValidLocksCompute'
    priority = 'priority'
    project = ProjectWithoutDataset
    projectIdCompute = 'projectIdCompute'
    readPermissionsFromLabels = 'readPermissionsFromLabels'
    status = 'status'
    statusCompute = 'statusCompute'
    toBeLabeledBy = ProjectUser
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
