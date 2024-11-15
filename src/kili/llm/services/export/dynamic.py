"""Handle LLM_INSTR_FOLLOWING project exports."""

import logging
from typing import Dict, List, Union

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
    "jsonResponse",  # This is needed to keep annotations
    "labelType",
    "modelName",
]


class LLMDynamicExporter:
    """Handle exports of LLM_RLHF projects."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def export(
        self, assets: List[Dict], json_interface: Dict
    ) -> List[Dict[str, Union[List[str], str]]]:
        """Asset content depends of each label."""
        export_res = []
        for asset in assets:
            # obfuscate models here
            obfuscated_models = {}
            for index, asset_project_model in enumerate(asset["assetProjectModels"]):
                obfuscated_models[asset_project_model["id"]] = f"{chr(65 + index)}"
            for label in asset["labels"]:
                result = {}
                chat_items = label["chatItems"]
                annotations = label["annotations"]
                rounds = self._build_rounds(chat_items, annotations, json_interface)
                for step, round in enumerate(rounds):
                    raw_data = _format_raw_data(
                        round["context"]
                        + round["pre_prompts"]
                        + [round["prompt"]]
                        + round["completion"],
                        label["id"],
                        obfuscated_models,
                    )
                    result[f"{step}"] = {
                        "external_id": asset["externalId"],
                        "metadata": asset["jsonMetadata"],
                        "models": _format_models_object(
                            asset["assetProjectModels"], obfuscated_models
                        ),
                        "labels": [
                            {
                                "author": label["author"]["email"],
                                "created_at": label["createdAt"],
                                "label_type": label["labelType"],
                                "label": _format_json_response(
                                    json_interface["jobs"],
                                    round["annotations"],
                                    round["completion"],
                                    obfuscated_models,
                                ),
                            }
                        ],
                        "raw_data": raw_data,
                        "status": asset["status"],
                    }
                export_res.append(result)
        return export_res

    def _get_round_winner(self, completions, annotations, json_interface):
        """Get the winner completion.

        Find the first comparison job in the json_interface and return the completion that has an annotation of this job targeting it.
        """
        comparison_job = None
        comparison_job_name = None
        for job_name, job in json_interface["jobs"].items():
            if job["mlTask"] == "COMPARISON":
                comparison_job = job
                comparison_job_name = job_name
                break
        if comparison_job is None:
            raise ValueError("No comparison job found in json_interface")

        winnerId = None
        for annotation in annotations:
            if annotation["job"] == comparison_job_name:
                winnerId = annotation["annotationValue"]["choice"]["firstId"]

        if winnerId is None:
            raise ValueError(
                f"Job {comparison_job_name} is used to create context, but no related annotations found"
            )
        res = list(filter(lambda completion: completion["id"] == winnerId, completions))
        return res[0] if len(res) > 0 else None

    def _init_round(self, context):
        return {
            "context": context,
            "prompt": None,
            "pre_prompts": [],
            "completion": [],
            "annotations": [],
        }

    def _build_rounds(self, chat_items, annotations, json_interface):
        """A round is composed of a prompt with n pre-prompts and n completions."""
        dict_chat_items = {}
        for chat_item in chat_items:
            if dict_chat_items.get(chat_item["parentId"]) is None:
                dict_chat_items[chat_item["parentId"]] = []
            dict_chat_items[chat_item["parentId"]].append(chat_item)
        rounds = []
        parent_target = None
        has_children = True
        current_round = self._init_round([])

        while has_children:
            nodes = dict_chat_items.get(parent_target)
            if nodes is None or len(nodes) == 0:
                has_children = False
                continue
            node = nodes[0]
            if node["role"].lower() == "system":
                current_round["pre_prompts"].append(node)
                parent_target = node["id"]
                current_round["annotations"] += [
                    annotation
                    for annotation in annotations
                    if annotation["chatItemId"] == node["id"]
                ]
                continue

            if node["role"].lower() == "user":
                current_round["prompt"] = node
                parent_target = node["id"]
                current_round["annotations"] += [
                    annotation
                    for annotation in annotations
                    if annotation["chatItemId"] == node["id"]
                ]
                continue

            if node["role"].lower() == "assistant":
                has_children = False
                if dict_chat_items.get(parent_target) is None:
                    continue
                for chat_item in dict_chat_items[parent_target]:
                    current_round["completion"].append(chat_item)
                    current_round["annotations"] += [
                        annotation
                        for annotation in annotations
                        if annotation["chatItemId"] == chat_item["id"]
                    ]
                    if not has_children and dict_chat_items.get(chat_item["id"]) is not None:
                        has_children = True
                        parent_target = chat_item["id"]

                rounds.append(current_round)
                new_context = (
                    current_round["context"]
                    + current_round["pre_prompts"]
                    + [
                        current_round["prompt"],
                        self._get_round_winner(
                            current_round["completion"],
                            current_round["annotations"],
                            json_interface,
                        ),
                    ]
                )
                current_round = self._init_round(new_context)
                continue

            raise ValueError(f"Role {node['role']} not supported")
        if current_round["prompt"] is not None:
            rounds.append(current_round)
        return rounds


def _format_classification_annotation(annotation):
    return annotation["annotationValue"]["categories"]


def _format_transcription_annotation(annotation):
    return annotation["annotationValue"]["text"]


def _format_comparison_annotation(annotation, completions, job, obfuscated_models):
    """Return A_X or B_X depending of the evaluation completion and its score."""
    model_id = None
    for completion in completions:
        if annotation["annotationValue"]["choice"]["firstId"] == completion["id"]:
            model_id = completion["modelId"]
            break

    if model_id is None:
        raise ValueError(f"Failed to found model of annotation {annotation['id']}")

    iteration = 0
    for _comparison_code, comparison_note in job["content"]["options"].items():
        iteration += 1
        if comparison_note["name"] == annotation["annotationValue"]["choice"]["code"]:
            break

    return f"{obfuscated_models[model_id]}_{iteration}"


def _format_json_response(
    jobs_config: Dict, annotations: List[Dict], completions: List[Dict], obfuscated_models: Dict
) -> Dict[str, Union[str, List[str]]]:
    result = {}
    for annotation in annotations:
        formatted_response = None
        job = jobs_config[annotation["job"]]
        if job["mlTask"] == "CLASSIFICATION":
            formatted_response = _format_classification_annotation(annotation)
        elif job["mlTask"] == "TRANSCRIPTION":
            formatted_response = _format_transcription_annotation(annotation)
        elif job["mlTask"] == "COMPARISON":
            formatted_response = _format_comparison_annotation(
                annotation, completions, job, obfuscated_models
            )

        if formatted_response is None:
            logging.warning(
                f"Annotation with job {annotation['job']} with mlTask {job['mlTask']} not supported. Ignored in the export."
            )
        else:
            result[annotation["job"]] = formatted_response

    return result


def _format_raw_data(chat_items, label_id, obfuscated_models):
    raw_data = []
    for chat_item in chat_items:
        raw_data.append(
            {
                "content": chat_item["content"],
                "role": chat_item["role"].lower(),
                "chat_id": label_id,
                "id": chat_item["id"],
                "model": obfuscated_models[chat_item["modelId"]]
                if chat_item["modelId"] in obfuscated_models
                else None,
            }
        )
    return raw_data


def _format_models_object(models, obfuscated_models):
    res = {}
    for model in models:
        model_configuration = {
            "id": model["id"],
            "projectModelId": model["projectModelId"],
            "configuration": model["configuration"],
        }
        res[obfuscated_models[model["id"]]] = model_configuration

    return res
