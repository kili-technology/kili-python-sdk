"""Label gateway common."""
from typing import Dict, List

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.label import LabelId
from kili.domain.types import ListOrTuple
from kili.exceptions import GraphQLError

from .operations import get_annotations_query


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
