"""Label gateway common."""
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.label.operations import (
    get_annotations_partial_query,
)


def get_annotation_fragment():
    """Generates a fragment to get all annotations and their values."""
    return get_annotations_partial_query(
        annotation_fragment=fragment_builder(("__typename", "id", "job", "path", "labelId")),
        classification_annotation_fragment=fragment_builder(("annotationValue.categories",)),
        ranking_annotation_fragment=fragment_builder(
            (
                "annotationValue.orders.elements",
                "annotationValue.orders.rank",
            )
        ),
        transcription_annotation_fragment=fragment_builder(("annotationValue.text",)),
        video_annotation_fragment=fragment_builder(
            (
                "frames.start",
                "frames.end",
                "keyAnnotations.id",
                "keyAnnotations.frame",
            )
        ),
        video_classification_annotation_fragment=fragment_builder(
            ("keyAnnotations.annotationValue.categories",)
        ),
        video_object_detection_annotation_fragment=fragment_builder(
            (
                "keyAnnotations.annotationValue.vertices.x",
                "keyAnnotations.annotationValue.vertices.y",
                "name",
                "mid",
                "category",
            )
        ),
        video_transcription_annotation_fragment=fragment_builder(
            ("keyAnnotations.annotationValue.text",)
        ),
    )
