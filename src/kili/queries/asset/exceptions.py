"""
Asset queries related exceptions
"""


class MissingPropertyError(ValueError):
    """Raised when trying to download an asset media with a missing fiels"""
