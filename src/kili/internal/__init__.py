"""
Module for methods and classes that are for internal use by Kili Technology only.
"""

from ..mutations.organization import MutationsOrganization


class KiliInternal(MutationsOrganization):
    """Inherit classes for internal use by Kili Technology only."""

    def __init__(self, kili):
        """Initializes the class.

        Args:
            kili: Kili object
        """
        self.kili = kili
        super().__init__(self.kili.auth)
