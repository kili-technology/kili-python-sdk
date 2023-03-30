"""Queries of data connection mutations."""

from .fragments import DATA_CONNECTION_FRAGMENT

GQL_ADD_PROJECT_DATA_CONNECTION = """
mutation addDataConnection($data: DataConnectionInput!) {
  data: addDataConnection(data: $data) {
    id
  }
}
"""

GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES = f"""
mutation computeDifferences($where: DataConnectionIdWhere!, $data: DataConnectionComputeDifferencesPayload) {{
  data: computeDifferences(where: $where, data: $data) {{
    {DATA_CONNECTION_FRAGMENT}
  }}
}}
"""

GQL_VALIDATE_DATA_DIFFERENCES = f"""
mutation validateDataDifferences($where: ValidateDataDifferencesWhere!, $processingParameters: String) {{
  data: validateDataDifferences(where: $where, processingParameters: $processingParameters) {{
    {DATA_CONNECTION_FRAGMENT}
  }}
}}
"""
