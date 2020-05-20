from enum import Enum


class Organization(Enum):
    id = 'id'
    address = 'address'
    city = 'city'
    country = 'country'
    name = 'name'
    zipCode = 'zipCode'


class User(Enum):
    id = 'id'
    activated = 'activated'
    createdAt = 'createdAt'
    email = 'email'
    name = 'name'
    organization = Organization
    organizationRole = 'organizationRole'
    updatedAt = 'updatedAt'


class ProjectUser(Enum):
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


class Project(Enum):
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
    numberOfLatestLabels = 'numberOfLatestLabels'
    numberOfRoles = 'numberOfRoles'
    roles = ProjectUser
    title = 'title'
    titleAndDescription = 'titleAndDescription'
    updatedAt = 'updatedAt'
    useHoneyPot = 'useHoneyPot'


class Label(Enum):
    id = 'id'
    author = User
    createdAt = 'createdAt'
    honeypotMark = 'honeypotMark'
    isLatestLabelForUser = 'isLatestLabelForUser'
    isLatestDefaultLabelForUser = 'isLatestDefaultLabelForUser'
    jsonResponse = 'jsonResponse'
    labelType = 'labelType'
    modelName = 'modelName'
    numberOfAnnotations = 'numberOfAnnotations'
    secondsToLabel = 'secondsToLabel'
    skipped = 'skipped'
    totalSecondsToLabel = 'totalSecondsToLabel'


class Lock(Enum):
    id = 'id'
    author = ProjectUser
    createdAt = 'createdAt'
    lockype = 'lockType'


class Asset(Enum):
    id = 'id'
    consensusMark = 'consensusMark'
    content = 'content'
    createdAt = 'createdAt'
    duration = 'duration'
    externalId = 'externalId'
    honeypotMark = 'honeypotMark'
    isHoneypot = 'isHoneypot'
    isUsedForConsensus = 'isUsedForConsensus'
    jsonMetadata = 'jsonMetadata'
    labels = Label
    locks = Lock
    numberOfValidLocks = 'numberOfValidLocks'
    priority = 'priority'
    project = Project
    status = 'status'
    toBeLabeledBy = User
    updatedAt = 'updatedAt'
