from .fragments import PROJECT_FRAGMENT, PROJECT_FRAGMENT_ID, ROLE_FRAGMENT


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
    $consensusMark: Float
    $consensusTotCoverage: Int
    $description: String
    $honeypotMark: Float
    $instructions: String
    $interfaceCategory: InterfaceCategory
    $inputType: InputType
    $jsonInterface: String
    $minConsensusSize: Int
    $numberOfAssets: Int
    $numberOfAssetsWithSkippedLabels: Int
    $numberOfRemainingAssets: Int
    $numberOfReviewedAssets: Int
    $projectID: ID!
    $title: String
) {{
  data: updatePropertiesInProject(
    where: {{
      id: $projectID
    }},
    data: {{
      consensusMark: $consensusMark
      consensusTotCoverage: $consensusTotCoverage
      description: $description
      honeypotMark: $honeypotMark
      instructions: $instructions
      interfaceCategory: $interfaceCategory
      inputType: $inputType
      jsonInterface: $jsonInterface
      minConsensusSize: $minConsensusSize
      numberOfAssets: $numberOfAssets
      numberOfAssetsWithSkippedLabels: $numberOfAssetsWithSkippedLabels
      numberOfRemainingAssets: $numberOfRemainingAssets
      numberOfReviewedAssets: $numberOfReviewedAssets
      title: $title
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

GQL_UPDATE_PROPERTIES_IN_ROLE = f'''
mutation(
    $roleID: ID!
    $projectID: ID!
    $userID: ID!
    $role: ProjectRole!
) {{
  
  data: updatePropertiesInRole(
    where: {{roleID: $roleID}}
    data: {{
      projectID: $projectID
      userID: $userID
      role: $role
    }}) {{
      {ROLE_FRAGMENT}
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
