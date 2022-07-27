"""
Queries of project mutations
"""

from .fragments import (
    PROJECT_FRAGMENT,
    PROJECT_FRAGMENT_ID,
    PROJECT_FRAGMENT_PUBLIC_TOKEN,
    ROLE_FRAGMENT,
)

GQL_APPEND_TO_ROLES = f"""
mutation($data: AppendToRolesData!, $where: ProjectWhere!) {{
  data: appendToRoles(
    data: $data
    where: $where
  ) {{
      {PROJECT_FRAGMENT}
  }}
}}
"""

GQL_UPDATE_PROPERTIES_IN_PROJECT = f"""
mutation(
    $consensusMark: Float
    $consensusTotCoverage: Int
    $description: String
    $honeypotMark: Float
    $instructions: String
    $inputType: InputType
    $jsonInterface: String
    $metadataTypes: JSON
    $minConsensusSize: Int
    $numberOfAssets: Int
    $numberOfSkippedAssets: Int
    $numberOfRemainingAssets: Int
    $numberOfReviewedAssets: Int
    $projectID: ID!
    $reviewCoverage: Int
    $title: String
    $useHoneyPot: Boolean
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
      inputType: $inputType
      jsonInterface: $jsonInterface
      metadataTypes: $metadataTypes
      minConsensusSize: $minConsensusSize
      numberOfAssets: $numberOfAssets
      numberOfSkippedAssets: $numberOfSkippedAssets
      numberOfRemainingAssets: $numberOfRemainingAssets
      numberOfReviewedAssets: $numberOfReviewedAssets
      reviewCoverage: $reviewCoverage
      title: $title
      useHoneyPot: $useHoneyPot
    }}
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_CREATE_PROJECT = f"""
mutation(
    $data: CreateProjectData!
  ) {{
  data: createProject(
    data: $data
  ) {{
      {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_MAKE_PROJECT_PUBLIC = f"""
mutation($where: ProjectWhere!) {{
  data: makeProjectPublic(where: $where) {{
    {PROJECT_FRAGMENT_PUBLIC_TOKEN}
  }}
}}
"""

GQL_UPDATE_PROPERTIES_IN_ROLE = f"""
mutation(
    $roleID: ID!
    $projectID: ID!
    $userID: ID!
    $role: ProjectRole!
) {{
  data: updatePropertiesInRole(
    where: {{id: $roleID}}
    data: {{
      projectID: $projectID
      userID: $userID
      role: $role
    }}) {{
      {ROLE_FRAGMENT}
  }}
}}
"""

GQL_DELETE_FROM_ROLES = f"""
mutation($where: ProjectUserWhere!) {{
  data: deleteFromRoles(where: $where) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER = f"""
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
"""

GQL_DELETE_PROJECT = f"""
mutation($projectID: ID!) {{
  data: deleteProject(where: {{
      id: $projectID
    }}
    ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_PROJECT_DELETE_ASYNCHRONOUSLY = """
mutation($where: ProjectWhere!) {
  data: deleteProjectAsynchronously(where: $where)
}
"""
