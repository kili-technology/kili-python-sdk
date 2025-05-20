from kili_formats.format.geojson.exceptions import (
    ConversionError,
)

test_cases = [
    (
        "Cross segments #1",
        [
            {"x": 0, "y": 0},
            {"x": 1, "y": 1},
            {"x": 1, "y": 0},
            {"x": 0, "y": 1},
        ],
        ConversionError,
    ),
    (
        "Cross segments #2",
        [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 0, "y": 1},
            {"x": 1, "y": 1},
        ],
        ConversionError,
    ),
    (
        "Cross segments #3",
        [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 1, "y": 0},
            {"x": 1, "y": 1},
        ],
        ConversionError,
    ),
    (
        "Cross segments #4",
        [
            {"x": 0, "y": 0},
            {"x": 2, "y": 2},
            {"x": 2, "y": 0},
            {"x": 0, "y": 2},
        ],
        ConversionError,
    ),
    (
        "Cross segments #5",
        [
            {"x": 0, "y": 0},
            {"x": 2, "y": 0},
            {"x": 0, "y": 2},
            {"x": 2, "y": 2},
        ],
        ConversionError,
    ),
    (
        "Cross segments #6",
        [
            {"x": 0, "y": 0},
            {"x": 0, "y": 2},
            {"x": 2, "y": 0},
            {"x": 2, "y": 2},
        ],
        ConversionError,
    ),
]
