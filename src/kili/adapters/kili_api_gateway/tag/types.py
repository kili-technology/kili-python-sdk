"""Types for the Tag-related Kili API gateway functions."""
from dataclasses import dataclass

from kili.domain.tag import TagId


@dataclass
class UpdateTagReturnData:
    """Return data."""

    affected_rows: int
    updated_tag_id: TagId
