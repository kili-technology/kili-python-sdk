"""
Import service exceptions
"""


class MimeTypeError(Exception):
    """
    Raised when the mime type of a file is not found or
    is not compatible with the project type to import in
    """


class ImportValidationError(Exception):
    """
    Raised when data given to import does not follow a right format
    """


class UploadFromLocalDataForbiddenError(Exception):
    """
    Raised when data given to import does not follow a right format
    """


class BatchImportError(Exception):
    """
    Raised when an error occurs during the import a batch of assets
    """