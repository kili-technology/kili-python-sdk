# Feature is still under development and is not yet suitable for use by general users.
"""Exceptions for label response module."""


class JobNotExistingError(Exception):
    """Raised when the job does not exist."""

    def __init__(self, job_name: str) -> None:
        """Init."""
        super().__init__(f"Job named '{job_name}' does not exist.")


class AttributeNotCompatibleWithJobError(Exception):
    """Raised when the attribute is not compatible with the job."""

    def __init__(self, attribute_name: str) -> None:
        """Init."""
        super().__init__(f"The attribute '{attribute_name}' is not compatible with the job.")


class InvalidMutationError(Exception):
    """Raised when the mutation is invalid."""
