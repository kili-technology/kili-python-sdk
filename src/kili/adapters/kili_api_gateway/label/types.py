"""Types for the label-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class UpdateLabelData:
    """Data to update a label."""

    is_sent_back_to_queue: Optional[bool]
    json_response: Optional[Dict]
    model_name: Optional[str]
    seconds_to_label: Optional[float]
