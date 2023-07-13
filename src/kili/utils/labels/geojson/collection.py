from typing import Dict, List, Literal, Union


def features_list_to_feature_collection(
    features: List[Dict],
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
    """Convert a list of features to a feature collection."""
    return {"type": "FeatureCollection", "features": features}
