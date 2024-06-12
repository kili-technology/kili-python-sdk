"""Label gateway common."""
from typing import Dict, List

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.label.operations import (
    get_annotations_partial_query,
    get_annotations_query,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.label import LabelId
from kili.domain.types import ListOrTuple
from kili.exceptions import GraphQLError


def get_annotation_fragment():
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


def list_annotations(
    graphql_client: GraphQLClient,
    label_id: LabelId,
    *,
    annotation_fields: ListOrTuple[str],
    classification_annotation_fields: ListOrTuple[str] = (),
    ranking_annotation_fields: ListOrTuple[str] = (),
    transcription_annotation_fields: ListOrTuple[str] = (),
    video_annotation_fields: ListOrTuple[str] = (),
    video_classification_fields: ListOrTuple[str] = (),
    video_object_detection_fields: ListOrTuple[str] = (),
    video_transcription_fields: ListOrTuple[str] = (),
) -> List[Dict]:
    """List annotations for a label."""
    query = get_annotations_query(
        annotation_fragment=fragment_builder(annotation_fields),
        classification_annotation_fragment=fragment_builder(classification_annotation_fields),
        ranking_annotation_fragment=fragment_builder(ranking_annotation_fields),
        transcription_annotation_fragment=fragment_builder(transcription_annotation_fields),
        video_annotation_fragment=fragment_builder(video_annotation_fields),
        video_classification_annotation_fragment=fragment_builder(video_classification_fields),
        video_object_detection_annotation_fragment=fragment_builder(video_object_detection_fields),
        video_transcription_annotation_fragment=fragment_builder(video_transcription_fields),
    )
    variables = {"where": {"labelId": label_id}}

    try:
        result = graphql_client.execute(query, variables)
    except GraphQLError as err:
        if "Cannot query field" in str(err):  # not available on LTS
            return []
        raise

    return result["data"]
