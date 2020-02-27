from .fragments import PROJECT_FRAGMENT, PROJECT_FRAGMENT_ID

GQL_CREATE_PROJECT = f'''
mutation(
    $title: String!
    $description: String!
    $useHoneyPot: Boolean!
    $interfaceJsonSettings: String!
) {{
  data: createProject(
  title: $title
  description: $description
  useHoneyPot: $useHoneyPot
  interfaceJsonSettings: $interfaceJsonSettings) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_APPEND_TO_ROLES = f'''
mutation($projectID: ID!, $userEmail: String!, $role: ProjectRole!) {{
  data: appendToRoles(
    projectID: $projectID
    userEmail: $userEmail
    role: $role) {{
      {PROJECT_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_PROPERTIES_IN_PROJECT = f'''
mutation(
    $projectID: ID!
    $title: String
    $description: String
    $minConsensusSize: Int
    $consensusTotCoverage: Int
    $numberOfAssets: Int
    $numberOfRemainingAssets: Int
    $numberOfAssetsWithSkippedLabels: Int
    $numberOfReviewedAssets: Int
    $numberOfLatestLabels: Int
    $consensusMark: Float
    $honeypotMark: Float
    $instructions: String
    $jsonSettings: String
) {{
  data: updatePropertiesInProject(
    where: {{id: $projectID}},
    data: {{
      title: $title
      description: $description
      minConsensusSize: $minConsensusSize
      consensusTotCoverage: $consensusTotCoverage
      numberOfAssets: $numberOfAssets
      numberOfRemainingAssets: $numberOfRemainingAssets
      numberOfAssetsWithSkippedLabels: $numberOfAssetsWithSkippedLabels
      numberOfReviewedAssets: $numberOfReviewedAssets
      numberOfLatestLabels: $numberOfLatestLabels
      consensusMark: $consensusMark
      honeypotMark: $honeypotMark
      instructions: $instructions
      jsonSettings: $jsonSettings
    }}
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''


GQL_CREATE_EMPTY_PROJECT = f'''
mutation($userID: ID!) {{
  data: createEmptyProject(userID: $userID) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_UPDATE_PROJECT = f'''
mutation(
    $projectID: ID!
    $title: String!
    $description: String
    $interfaceCategory: InterfaceCategory
    $inputType: InputType
    $consensusTotCoverage: Int
    $minConsensusSize: Int
    $maxWorkerCount: Int
    $minAgreement: Int
    $useHoneyPot: Boolean
    $instructions: String
) {{
  data: updateProject(
    projectID: $projectID
    title: $title
    description: $description
    interfaceCategory: $interfaceCategory
    inputType: $inputType
    consensusTotCoverage: $consensusTotCoverage
    minConsensusSize: $minConsensusSize
    maxWorkerCount: $maxWorkerCount
    minAgreement: $minAgreement
    useHoneyPot: $useHoneyPot
    instructions: $instructions) {{
      {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_UPDATE_ROLE = f'''
mutation(
    $roleID: ID!
    $projectID: ID!
    $userID: ID!
    $role: ProjectRole!
) {{
  data: updateRole(
    roleID: $roleID
    projectID: $projectID
    userID: $userID
    role: $role) {{
      {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_DELETE_FROM_ROLES = f'''
mutation($roleID: ID!) {{
  data: deleteFromRoles(roleID: $roleID) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER = f'''
mutation(
    $projectID: ID!
    $totalDuration: Int
    $numberOfLabeledAssets: Int
    $consensusMark: Float
    $honeypotMark: Float
) {{
  data: updatePropertiesInProjectUser(
    where: {{id: $projectID}},
    data: {{
      totalDuration: $totalDuration
      numberOfLabeledAssets: $numberOfLabeledAssets
      consensusMark: $consensusMark
      honeypotMark: $honeypotMark
    }}
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''
