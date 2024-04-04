"""Import service types."""

from typing import List, Union

from typing_extensions import TypedDict


class AssetLike(TypedDict, total=False):
    """General type of an asset object through the import functions."""

    content: Union[str, bytes, dict]
    multi_layer_content: Union[List[dict], None]
    json_content: Union[dict, str, list]
    external_id: str
    json_metadata: Union[str, dict]
    is_honeypot: bool
    id: str


class KiliResolverAsset(AssetLike, TypedDict, total=True):
    """Type of an asset object to be sent in Kili resolvers."""

    content: Union[str, bytes]
    multi_layer_content: List[dict]
    json_content: Union[dict, str, list]
    external_id: str
    json_metadata: Union[str, dict]
    is_honeypot: bool
    id: str
