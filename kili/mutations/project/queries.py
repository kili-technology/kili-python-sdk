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

GQL_CREATE_PROJECT = f'''
mutation(
    $description: String!
    $inputType: InputType!
    $jsonInterface: String!
    $projectType: ProjectType
    $title: String!
    $userID: ID!
  ) {{
  data: createProject(
    description: $description
    inputType: $inputType
    jsonInterface: $jsonInterface
    projectType: $projectType
    title: $title
    userID: $userID) {{
      {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_MAKE_PROJECT_PUBLIC = f'''
mutation(
    $projectID: ID!
  ) {{
  data: makeProjectPublic(
    where: {{
      id: $projectID
  }}) {{
      publicToken
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
    $projectUserID: ID!
    $totalDuration: Int
    $numberOfLabeledAssets: Int
    $starred: Boolean
    $consensusMark: Float
    $honeypotMark: Float
) {{
  data: updatePropertiesInProjectUser(
    where: {{id: $projectUserID}},
    data: {{
      totalDuration: $totalDuration
      numberOfLabeledAssets: $numberOfLabeledAssets
      starred: $starred
      consensusMark: $consensusMark
      honeypotMark: $honeypotMark
    }}
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''

GQL_DELETE_PROJECT = f'''
mutation($projectID: ID!) {{
  data: deleteProject(where: {{
      id: $projectID
    }}
    ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
'''
