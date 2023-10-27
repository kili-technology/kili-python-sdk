"""GraphQL User operations."""


def get_users_query(fragment: str) -> str:
    """Return the GraphQL users query."""
    return f"""
        query users($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
            data: users(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """


def get_current_user_query(fragment: str) -> str:
    """Return the GraphQL current user query."""
    return f"""
      query me {{
          data: me {{
              {fragment}
          }}
      }}
    """


def get_create_user_mutation(fragment: str) -> str:
    """Return the GraphQL create user mutation."""
    return f"""
      mutation(
          $data: CreateUserData!
      ) {{
        data: createUser(
            data: $data
        ) {{
          {fragment}
        }}
      }}
    """


def get_update_password_mutation(fragment: str) -> str:
    """Return the GraphQL update password mutation."""
    return f"""
mutation(
    $data: UpdatePasswordData!
    $where: UserWhere!
) {{
  data: updatePassword(
    data: $data
    where: $where
  ) {{
    {fragment}
  }}
}}
"""


def get_update_user_mutation(fragment: str) -> str:
    """Return the GraphQL update user mutation."""
    return f"""
      mutation updatePropertiesInUser( $data: UserData!, $where: UserWhere!) {{
        data: updatePropertiesInUser( data: $data,  where: $where) {{
          {fragment}
        }}
      }}
      """


GQL_COUNT_USERS = """
    query countUsers($where: UserWhere!) {
        data: countUsers(where: $where)
    }
    """


def get_reset_password_mutation(fragment: str) -> str:
    """Return the GraphQL reset password mutation."""
    return f"""
    mutation($where: UserWhere!) {{
      data: resetPassword(where: $where) {{
        {fragment}
      }}
    }}
"""
