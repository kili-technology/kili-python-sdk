"""
Queries of user mutations
"""

from .fragments import USER_FRAGMENT

GQL_CREATE_USER = f"""
mutation(
    $data: CreateUserData!
) {{
  data: createUser(
      data: $data
  ) {{
    {USER_FRAGMENT}
  }}
}}
"""

GQL_UPDATE_PASSWORD = f"""
mutation(
    $data: UpdatePasswordData!
    $where: UserWhere!
) {{
  data: updatePassword(
    data: $data
    where: $where
  ) {{
    {USER_FRAGMENT}
  }}
}}
"""

GQL_RESET_PASSWORD = f"""
mutation($where: UserWhere!) {{
  data: resetPassword(where: $where) {{
    {USER_FRAGMENT}
  }}
}}
"""

GQL_UPDATE_PROPERTIES_IN_USER = f"""
mutation(
    $email: String!
    $firstname: String
    $lastname: String
    $organizationId: String
    $organizationRole: OrganizationRole
    $activated: Boolean
) {{
  data: updatePropertiesInUser(
    where: {{email: $email}}
    data: {{
      firstname: $firstname
      lastname: $lastname
      email: $email
      organizationId: $organizationId
      organizationRole: $organizationRole
      activated: $activated
    }}
  ) {{
    {USER_FRAGMENT}
  }}
}}
"""
