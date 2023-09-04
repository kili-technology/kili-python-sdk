"""Asset queries related exceptions."""


class MissingPropertyError(Exception):
    """Raised when trying to download an asset media with a missing field."""


class DownloadNotAllowedError(Exception):
    """Raised when trying to download assets on a project connected to a cloud storage."""
