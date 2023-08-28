"""Module for common argument validators across client methods."""

import warnings


def disable_tqdm_if_as_generator(as_generator: bool, disable_tqdm: bool):
    """Disable tqdm in user-facing queries method if the return type is asked as a generator."""
    if as_generator and not disable_tqdm:
        disable_tqdm = True
        warnings.warn(
            "tqdm has been forced disabled because its behavior is not compatible with the"
            " generator return type",
            stacklevel=2,
        )
    return disable_tqdm
