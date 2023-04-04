"""Data integration queries."""

GQL_GET_DATA_INTEGRATION_FOLDER_AND_SUBFOLDERS = """
query getFoldersAndSubfolders($dataIntegrationId: ID!, $rootFolder: String) {
  data: getFoldersAndSubfolders(dataIntegrationId: $dataIntegrationId, rootFolder: $rootFolder)
}
"""
