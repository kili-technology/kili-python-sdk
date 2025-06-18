"""Label gateway common."""
from typing import Dict

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset.formatters import load_asset_json_fields
from kili.adapters.kili_api_gateway.asset.operations import get_assets_query
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.label.operations import (
    get_annotations_partial_query,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset.asset import AssetId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound


def get_asset(
    graphql_client: GraphQLClient,
    http_client: HttpClient,
    asset_id: AssetId,
    fields: ListOrTuple[str],
) -> Dict:
    """Get asset."""
    fragment = fragment_builder(fields)
    query = get_assets_query(fragment)
    result = graphql_client.execute(
        query=query, variables={"where": {"id": asset_id}, "first": 1, "skip": 0}
    )
    assets = result["data"]

    if len(assets) == 0:
        raise NotFound(
            f"asset ID: {asset_id}. The asset does not exist or you do not have access to it."
        )
    return load_asset_json_fields(assets[0], fields, http_client=http_client)


def get_annotation_fragment():
    """Generates a fragment to get all annotations and their values."""
    return get_annotations_partial_query(
        annotation_fragment=fragment_builder(("__typename", "id", "job", "path", "labelId")),
        classification_annotation_fragment=fragment_builder(
            ("annotationValue.categories", "chatItemId")
        ),
        ranking_annotation_fragment=fragment_builder(
            (
                "annotationValue.orders.elements",
                "annotationValue.orders.rank",
            )
        ),
        comparison_annotation_fragment=fragment_builder(
            (
                "annotationValue.choice.code",
                "annotationValue.choice.firstId",
                "annotationValue.choice.secondId",
                "chatItemId",
            )
        ),
        transcription_annotation_fragment=fragment_builder(("annotationValue.text", "chatItemId")),
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
                "keyAnnotations.annotationValue.vertices: verticesScalar",
                "name",
                "mid",
                "category",
            )
        ),
        video_transcription_annotation_fragment=fragment_builder(
            ("keyAnnotations.annotationValue.text",)
        ),
        object_detection_annotation_fragment=fragment_builder(
            ("category", "mid", "name", "annotationValue.vertices: verticesScalar")
        ),
    )
