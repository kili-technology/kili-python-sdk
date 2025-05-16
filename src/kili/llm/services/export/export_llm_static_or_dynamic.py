from typing import Dict, List, Optional, cast

from kili_formats import convert_from_kili_to_llm_static_or_dynamic_format
from kili_formats.types import ChatItem, Conversation, JobLevel

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway

CHAT_ITEMS_NEEDED_FIELDS = [
    "id",
    "content",
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
    "jsonResponse",
    "labelType",
    "modelName",
]


DEFAULT_JOB_LEVEL = JobLevel.ROUND


def get_model_name(model_id: Optional[str], project_models: List[Dict]) -> Optional[str]:
    try:
        return next(
            model["configuration"]["model"] for model in project_models if model["id"] == model_id
        )
    except (KeyError, StopIteration):
        return model_id


class LLMExporter:
    """Handle exports of LLM_STATIC and LLM_INSTR_FOLLOWING projects."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def export(self, assets: List[Dict], json_interface: Dict) -> List[Conversation]:
        return [self.format_asset(asset, json_interface) for asset in assets if asset.get("labels")]

    def format_asset(self, asset: Dict, json_interface: Dict) -> Conversation:
        label = asset["labels"][-1]
        chat_items = [
            {
                "id": chat_item["id"],
                "content": chat_item.get("content"),
                "externalId": chat_item.get("externalId") or chat_item["id"],
                "modelName": chat_item.get("modelName")
                or get_model_name(chat_item.get("modelId"), asset["assetProjectModels"]),
                "role": chat_item.get("role"),
            }
            for chat_item in (
                label.get("chatItems") or self.kili_api_gateway.list_chat_items(asset["id"])
            )
        ]

        metadata = {}
        if asset.get("assetProjectModels"):
            metadata["models"] = asset["assetProjectModels"]

        chat_items_without_ids = [
            cast(ChatItem, {k: v for k, v in chat_item.items() if k != "id"})
            for chat_item in chat_items
        ]

        return {
            "chatItems": chat_items_without_ids,
            "externalId": asset["externalId"],
            "label": convert_from_kili_to_llm_static_or_dynamic_format(
                annotations=label["annotations"],
                chat_items=chat_items,
                jobs=json_interface["jobs"],
            ),
            "labeler": label["author"]["email"],
            "metadata": metadata,
        }
