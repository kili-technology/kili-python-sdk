"""Service for exporting kili objects."""

from typing import Dict, List, Optional, Union

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset.asset import AssetFilters
from kili.domain.label import LabelType
from kili.domain.project import ProjectId

from .dynamic import LLMDynamicExporter
from .static import LLMStaticExporter

CHAT_ITEMS_NEEDED_FIELDS = [
    "id",
    "content",
    "createdAt",
    "modelId",
    "parentId",
    "role",
]

LABELS_NEEDED_FIELDS = [
    "annotations.id",
    "author.id",
    "author.email",
    "author.firstname",
    "author.lastname",
    *(f"chatItems.{field}" for field in CHAT_ITEMS_NEEDED_FIELDS),
    "createdAt",
    "id",
    "isLatestLabelForUser",
    "isSentBackToQueue",
    "jsonResponse",  # This is needed to keep annotations
    "labelType",
    "modelName",
]

ASSET_DYNAMIC_NEEDED_FIELDS = [
    "assetProjectModels.id",
    "assetProjectModels.configuration",
    "assetProjectModels.projectModelId",
    "content",
    "externalId",
    "jsonMetadata",
    *(f"labels.{field}" for field in LABELS_NEEDED_FIELDS),
    "status",
]

ASSET_STATIC_NEEDED_FIELDS = [
    "content",
    "externalId",
    "jsonMetadata",
    "labels.jsonResponse",
    "labels.author.id",
    "labels.author.email",
    "labels.author.firstname",
    "labels.author.lastname",
    "labels.createdAt",
    "labels.isLatestLabelForUser",
    "labels.isSentBackToQueue",
    "labels.labelType",
    "labels.modelName",
    "status",
]


def export(  # pylint: disable=too-many-arguments, too-many-locals
    kili_api_gateway: KiliAPIGateway,
    project_id: ProjectId,
    asset_filter: AssetFilters,
    disable_tqdm: Optional[bool],
    include_sent_back_labels: Optional[bool],
    label_type_in: List[LabelType],
) -> Optional[List[Dict[str, Union[List[str], str]]]]:
    """Export the selected assets with their labels into the required format, and save it into a file archive."""
    project = kili_api_gateway.get_project(project_id, ["id", "inputType", "jsonInterface"])
    input_type = project["inputType"]

    fields = get_fields_to_fetch(input_type)
    assets = list(
        kili_api_gateway.list_assets(asset_filter, fields, QueryOptions(disable_tqdm=disable_tqdm))
    )
    cleaned_assets = preprocess_assets(assets, include_sent_back_labels or False, label_type_in)

    if input_type == "LLM_RLHF":
        return LLMStaticExporter(kili_api_gateway).export(
            cleaned_assets, project_id, project["jsonInterface"]
        )
    if input_type == "LLM_INSTR_FOLLOWING":
        return LLMDynamicExporter(kili_api_gateway).export(cleaned_assets, project["jsonInterface"])
    raise ValueError(f'Project Input type "{input_type}" cannot be used for llm exports.')


def get_fields_to_fetch(input_type: str) -> List[str]:
    """Return the fields to fetch depending on the export type."""
    if input_type == "LLM_RLHF":
        return ASSET_STATIC_NEEDED_FIELDS
    return ASSET_DYNAMIC_NEEDED_FIELDS


def preprocess_assets(
    assets: List[Dict], include_sent_back_labels: bool, label_type_in: List[LabelType]
) -> List[Dict]:
    """Format labels in the requested format, and filter out autosave labels."""
    assets_in_format = []
    for asset in assets:
        if "labels" in asset:
            labels_of_asset = []
            for label in asset["labels"]:
                labels_of_asset.append(label)
                labels_of_asset = list(
                    filter(lambda label: label["labelType"] in label_type_in, labels_of_asset)
                )
                if not include_sent_back_labels:
                    labels_of_asset = list(
                        filter(lambda label: label["isSentBackToQueue"] is False, labels_of_asset)
                    )
            if len(labels_of_asset) > 0:
                asset["labels"] = labels_of_asset
                assets_in_format.append(asset)
    return assets_in_format
