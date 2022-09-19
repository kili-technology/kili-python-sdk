"""Import service types"""

from typing import List, Optional, Union

from typing_extensions import TypedDict


class AssetLike(TypedDict, total=False):
    """
    General type of an asset obejct through the import functions
    """

    content: Optional[str]
    json_content: Optional[Union[List[str], dict, str]]
    external_id: Optional[str]
    status: Optional[str]
    json_metadata: Optional[Union[str, dict]]
    is_honeypot: Optional[bool]


class KiliResolverAsset(TypedDict, total=True):
    """
    Type of an asset object to be sent in Kili resolvers
    """

    content: str
    json_content: str
    external_id: str
    status: str
    json_metadata: str
    is_honeypot: bool
