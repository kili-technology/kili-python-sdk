"""
Queries of data connection mutations
"""

GQL_ADD_PROJECT_DATA_CONNECTION = """
mutation ($data: DataConnectionInput!) {
  data: addDataConnection(data: $data) {
    id
  }
}
"""
