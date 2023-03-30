"""Service exceptions."""


class NotEnoughArgumentsSpecifiedError(ValueError):
    """Raised when there are not enough arguments specified in a service."""


class TooManyArgumentsSpecifiedError(ValueError):
    """Raised when there are too many arguments specified in a service."""
