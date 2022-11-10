"""Import service types"""

from typing import Union

from typing_extensions import TypedDict


class AssetLike(TypedDict, total=False):
    """
    General type of an asset obejct through the import functions
    """

    content: Union[str, bytes]
    json_content: Union[dict, str, list]
    external_id: str
    status: str
    json_metadata: Union[str, dict]
    is_honeypot: bool
    id: str


class KiliResolverAsset(AssetLike, TypedDict, total=True):
    """
    Type of an asset object to be sent in Kili resolvers
    """

    content: Union[str, bytes]
    json_content: Union[dict, str, list]
    external_id: str
    status: str
    json_metadata: Union[str, dict]
    is_honeypot: bool
    id: str
