"""Import service types"""

from typing import List, Optional, Union

from typing_extensions import TypedDict


class AssetToImport(TypedDict):
    """Asset to import."""

    content: Optional[str]
    json_content: Optional[Union[List[list], dict]]
    external_id: Optional[str]
    status: Optional[str]
    json_metadata: Optional[dict]
    is_honeypot: Optional[bool]
