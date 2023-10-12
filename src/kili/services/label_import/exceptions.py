"""Label import-specific errors."""


class LabelParsingError(ValueError):
    """Raised when there is a failure to parse a label."""


class MissingMetadataError(ValueError):
    """Raised when a metadata file is missing."""


class MissingTargetJobError(ValueError):
    """Raised when the target job is missing."""
