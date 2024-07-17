"""Import service exceptions."""


class MimeTypeError(Exception):
    """MimeTypeError.

    Raised when the mime type of a file is not found
    or not compatible with the project type to import in.
    """


class ImportValidationError(Exception):
    """Raised when data given to import does not follow a right format."""


class ImportFileConversionError(Exception):
    """Raised when an error occurs during processing a llm file for conversion."""


class UploadFromLocalDataForbiddenError(Exception):
    """Raised when data given to import does not follow a right format."""


class BatchImportError(Exception):
    """Raised when an error occurs during the import a batch of assets."""


class BatchImportPendingNotificationError(Exception):
    """Raised when the batch import is stil pending."""
