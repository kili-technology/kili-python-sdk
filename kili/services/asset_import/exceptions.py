class MimeTypeError(Exception):
    """
    Raised when the mime type of a file is not found or
    is not compatible with the project type to import in
    """


class FileNotFoundError(Exception):
    """
    Raised when a file is not found on the local machine
    """


class ImportValidationError(Exception):
    """
    Raised when data given to import does not follow a right format
    """
