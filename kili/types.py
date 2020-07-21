class Organization(object):
    id = 'id'
    address = 'address'
    city = 'city'
    country = 'country'
    name = 'name'
    zipCode = 'zipCode'


class User(object):
    id = 'id'
    activated = 'activated'
    createdAt = 'createdAt'
    email = 'email'
    name = 'name'
    organization = Organization
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
    user = User


class Project(object):
    id = 'id'
    author = User
    consensusMark = 'consensusMark'
    consensusTotCoverage = 'consensusTotCoverage'
    createdAt = 'createdAt'
    description = 'description'
    honeypotMark = 'honeypotMark'
    inputType = 'inputType'
    interfaceCategory = 'interfaceCategory'
    jsonInterface = 'jsonInterface'
    maxWorkerCount = 'maxWorkerCount'
    minAgreement = 'minAgreement'
    minConsensusSize = 'minConsensusSize'
    numberOfRemainingAssets = 'numberOfRemainingAssets'
    numberOfAssets = 'numberOfAssets'
    numberOfAssetsWithSkippedLabels = 'numberOfAssetsWithSkippedLabels'
    numberOfReviewedAssets = 'numberOfReviewedAssets'
    readPermissionsForAssetsAndLabels = 'readPermissionsForAssetsAndLabels'
    roles = ProjectUserWithoutProject
    title = 'title'
    titleAndDescription = 'titleAndDescription'
    updatedAt = 'updatedAt'
    useHoneyPot = 'useHoneyPot'


class ProjectUser(ProjectUserWithoutProject):
    project = Project


class Label(object):
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
    author = ProjectUser
    createdAt = 'createdAt'
    lockype = 'lockType'


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
    jsonMetadata = 'jsonMetadata'
    labels = Label
    locks = Lock
    numberOfValidLocks = 'numberOfValidLocks'
    numberOfValidLocksCompute = 'numberOfValidLocksCompute'
    priority = 'priority'
    project = Project
    projectIdCompute = 'projectIdCompute'
    readPermissionsFromLabels = 'readPermissionsFromLabels'
    status = 'status'
    statusCompute = 'statusCompute'
    toBeLabeledBy = User
    updatedAt = 'updatedAt'
