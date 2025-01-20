from typing import Dict, List, Optional, cast

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.llm import ChatItem, ChatItemRole, Conversation, ConversationLabel

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


class JobLevel:
    ROUND = "round"
    CONVERSATION = "conversation"
    COMPLETION = "completion"


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
            "label": self.format_llm_label(
                annotations=label["annotations"],
                chat_items=chat_items,
                jobs=json_interface["jobs"],
            ),
            "labeler": label["author"]["email"],
            "metadata": metadata,
        }

    def format_llm_label(
        self, annotations: List[Dict], chat_items: List[Dict], jobs: Dict
    ) -> ConversationLabel:
        formatted_label = {JobLevel.COMPLETION: {}, JobLevel.CONVERSATION: {}, JobLevel.ROUND: {}}

        for job_name, job in jobs.items():
            job_level = job.get("level", DEFAULT_JOB_LEVEL)

            if job_level == JobLevel.COMPLETION:
                job_label = self.format_completion_job(job_name, annotations, chat_items)
            elif job_level == JobLevel.CONVERSATION:
                job_label = self.format_conversation_job(job_name, annotations)
            elif job_level == JobLevel.ROUND:
                job_label = self.format_round_job(job_name, annotations, chat_items)
            else:
                raise ValueError(f"Unknown job level: {job_level}")

            if job_label:
                formatted_label[job_level][job_name] = job_label

        return cast(ConversationLabel, formatted_label)

    @staticmethod
    def format_completion_job(
        job_name: str, annotations: List[Dict], chat_items: List[Dict]
    ) -> Dict:
        id_to_external_id = {
            item["id"]: item.get("externalId") or item["id"] for item in chat_items
        }
        job_annotations = [
            annotation for annotation in annotations if annotation.get("job") == job_name
        ]
        return {
            id_to_external_id.get(annotation["chatItemId"]): annotation["annotationValue"]
            for annotation in job_annotations
        }

    def format_round_job(
        self, job_name: str, annotations: List[Dict], chat_items: List[Dict]
    ) -> Dict:
        id_to_external_id = {
            item["id"]: item.get("externalId") or item["id"] for item in chat_items
        }
        job_annotations = [
            annotation for annotation in annotations if annotation.get("job") == job_name
        ]
        user_chat_item_ids = [
            chat_item.get("external_id") or chat_item["id"]
            for chat_item in chat_items
            if chat_item["role"] == ChatItemRole.USER
        ]

        return {
            user_chat_item_ids.index(annotation["chatItemId"]): self.format_annotation_value(
                annotation["annotationValue"], id_to_external_id
            )
            for annotation in job_annotations
        }

    @staticmethod
    def format_conversation_job(job_name: str, annotations: List[Dict]) -> Dict:
        annotation = next(
            (annotation for annotation in annotations if annotation["job"] == job_name), None
        )
        if annotation:
            return annotation["annotationValue"]
        return {}

    @staticmethod
    def format_annotation_value(annotation_value: Dict, id_to_external_id: Dict[str, str]) -> Dict:
        if annotation_value.get("choice"):
            return {
                "code": annotation_value["choice"]["code"],
                "firstId": id_to_external_id.get(annotation_value["choice"]["firstId"]),
                "secondId": id_to_external_id.get(annotation_value["choice"]["secondId"]),
            }
        return annotation_value
