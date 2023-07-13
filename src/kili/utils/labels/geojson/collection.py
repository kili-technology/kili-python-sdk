from typing import Dict, List, Literal, Sequence, Union


def features_to_feature_collection(
    features: Sequence[Dict],
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
    """Convert a list of features to a feature collection.

    Args:
        features: a list of Geojson features.

    Returns:
        A Geojson feature collection.

    !!! Example
        ```python
        >>> features = [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-79.0, -3.0]},
                    'id': '1',
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-79.0, -3.0]},
                    'id': '2',
                }
            }
        ]
        >>> features_to_feature_collection(features)
        {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [-79.0, -3.0]},
                        'id': '1',
                    }
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [-79.0, -3.0]},
                        'id': '2',
                    }
                }
            ]
        }
        ```
    """
    return {"type": "FeatureCollection", "features": list(features)}
