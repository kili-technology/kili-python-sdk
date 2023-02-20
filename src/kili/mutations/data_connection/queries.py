"""
Queries of data connection mutations
"""

GQL_ADD_PROJECT_DATA_CONNECTION = """
mutation addDataConnection($data: DataConnectionInput!) {
  data: addDataConnection(data: $data) {
    id
  }
}
"""
