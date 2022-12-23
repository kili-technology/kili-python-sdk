"""
Export-related exceptions
"""


class DownloadError(Exception):
    """
    Exception thrown when the contents cannot be downloaded.
    """


class NoCompatibleJobError(Exception):
    """
    Exception thrown when there is no job compatible with the format.
    """


class NotCompatibleOptions(ValueError):
    """
    Exception thrown when export options are not compatible with the format.
    """


class NotCompatibleInputType(ValueError):
    """
    Exception thrown when project input type is not compatible with the export format.
    """
