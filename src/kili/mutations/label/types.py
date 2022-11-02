"""
Types for the label mutations
"""

from typing import Dict

from typing_extensions import Required, TypedDict


class AppendLabelData(TypedDict, total=False):
    """
    Data about a label to append
    """

    asset_id: Required[str]
    json_response: Required[Dict]
    author_id: str
    seconds_to_label: int
    modelName: str
