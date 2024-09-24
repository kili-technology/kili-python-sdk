"""Handle LLM_RLHF project exports."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.services.asset_import.helpers import SEPARATOR
from kili.services.export.format.llm.types import ExportLLMItem
from kili.use_cases.asset.media_downloader import MediaDownloader
from kili.utils.tempfile import TemporaryDirectory


class LLMStaticExporter:
    """Handle exports of LLM_RLHF projects."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def export(
        self, assets: List[Dict], project_id: ProjectId, json_interface: Dict
    ) -> List[Dict[str, Union[List[str], str]]]:
        """Assets are static, with n labels."""
        with TemporaryDirectory() as tmpdirname:
            assets = MediaDownloader(
                tmpdirname,
                project_id,
                False,
                "LLM_RLHF",
                self.kili_api_gateway.http_client,
            ).download_assets(assets)
            return self._process_llm_v1(assets, json_interface)

    def _process_llm_v1(
        self, assets: List[Dict], json_interface: Dict[str, Dict]
    ) -> List[Dict[str, Union[List[str], str]]]:
        result = []
        for asset in assets:
            result.append(
                {
                    "raw_data": _format_raw_data(asset),
                    "status": asset["status"],
                    "external_id": asset["externalId"],
                    "metadata": asset["jsonMetadata"],
                    "labels": list(
                        map(
                            lambda label: {
                                "author": label["author"]["email"],
                                "created_at": label["createdAt"],
                                "label_type": label["labelType"],
                                "label": _format_json_response(
                                    json_interface["jobs"], label["jsonResponse"]
                                ),
                            },
                            asset["labels"],
                        )
                    ),
                }
            )
        return result


def _format_json_response(
    jobs_config: Dict, json_response: Dict
) -> Dict[str, Union[str, List[str]]]:
    result = {}
    for job_name, job_value in json_response.items():
        job_config = jobs_config[job_name]
        if job_config is None:
            continue
        if job_config["mlTask"] == "CLASSIFICATION":
            result[job_name] = []
            for category in job_value["categories"]:
                result[job_name].append(category["name"])
                if "children" in category:
                    for child_name, child_value in _format_json_response(
                        jobs_config, category["children"]
                    ).items():
                        result[f"{job_name}.{category['name']}.{child_name}"] = child_value
        elif job_config["mlTask"] == "TRANSCRIPTION":
            result[job_name] = job_value["text"]
        else:
            logging.warning(f"Job {job_name} with mlTask {job_config['mlTask']} not supported")
    return result


def _format_raw_data(
    asset, step_number: Optional[int] = None, all_model_keys: Optional[bool] = False
) -> List[ExportLLMItem]:
    raw_data = []

    chat_id = asset["jsonMetadata"].get("chat_id", None)

    if (
        "chat_item_ids" in asset["jsonMetadata"]
        and isinstance(asset["jsonMetadata"]["chat_item_ids"], str)
        and len(asset["jsonMetadata"]["chat_item_ids"]) > 0
    ):
        chat_items_ids = str.split(asset["jsonMetadata"]["chat_item_ids"], SEPARATOR)
        if step_number is not None:
            chat_items_ids = chat_items_ids[step_number * 3 :]
    else:
        chat_items_ids = []

    if (
        "models" in asset["jsonMetadata"]
        and isinstance(asset["jsonMetadata"]["models"], str)
        and len(asset["jsonMetadata"]["models"]) > 0
    ):
        models = str.split(asset["jsonMetadata"]["models"], SEPARATOR)
    else:
        models = []
    with Path(asset["content"]).open(encoding="utf8") as file:
        data = json.load(file)
    version = data.get("version", None)
    if version == "0.1":
        prompts = data["prompts"]
        if step_number is not None:
            prompts = [prompts[step_number]]
        for index, prompt in enumerate(prompts):
            raw_data.append(
                ExportLLMItem(
                    {
                        "role": prompt.get("title", "user"),
                        "content": prompt["prompt"],
                        "id": _safe_pop(chat_items_ids),
                        "chat_id": chat_id,
                        "model": None,
                    }
                )
            )
            raw_data.extend(
                ExportLLMItem(
                    {
                        "role": completion.get("title", "assistant"),
                        "content": completion["content"],
                        "id": _safe_pop(chat_items_ids),
                        "chat_id": chat_id,
                        "model": models[index_completion]
                        if (
                            (index == len(prompts) - 1 or all_model_keys)
                            and len(models) > index_completion
                        )
                        else None,
                    }
                )
                for index_completion, completion in enumerate(prompt["completions"])
            )
    else:
        raise ValueError(f"Version {version} not supported")
    return raw_data


def _safe_pop(lst, index=0):
    try:
        return lst.pop(index)
    except IndexError:
        return None
