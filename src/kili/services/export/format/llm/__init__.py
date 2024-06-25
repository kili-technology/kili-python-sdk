"""Common code for the yolo exporter."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from kili.services.export.exceptions import NotCompatibleInputType
from kili.services.export.format.base import AbstractExporter
from kili.services.types import Job


class LLMExporter(AbstractExporter):
    """Common code for LLM exporters."""

    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""
        if not self.with_assets:
            raise ValueError("LLM export format requires assets to be downloaded.")

    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""
        if self.project["inputType"] != "LLM_RLHF":
            raise NotCompatibleInputType(
                f"Project with input type \"{self.project['inputType']}\" not compatible with LLM"
                " export format."
            )

    def _is_job_compatible(self, job: Job) -> bool:
        """Check job compatibility with the LLM format."""
        _ = job
        return True

    def _save_assets_export(self, assets: List[Dict], output_filename: Path) -> None:
        """Save the assets to a file and return the link to that file."""
        self.logger.info("Exporting to llm format...")

        export_json = json.dumps(assets, sort_keys=False, indent=4)
        with output_filename.open("wb") as output_file:
            output_file.write(export_json.encode("utf-8"))

    def process_and_save(
        self, assets: List[Dict], output_filename: Path
    ) -> Optional[List[Dict[str, Union[List[str], str]]]]:
        """LLM specific process and save."""
        result = self._process(assets)
        self._save_assets_export(result, output_filename)

    def process(self, assets: List[Dict]) -> List[Dict[str, Union[List[str], str]]]:
        """LLM specific process."""
        return self._process(assets)

    def _process(self, assets: List[Dict]) -> List[Dict[str, Union[List[str], str]]]:
        result = []
        for asset in assets:
            jobs_config = self.project["jsonInterface"]["jobs"]
            latest_label = asset["latestLabel"]
            result.append(
                {
                    "raw_data": _format_raw_data(asset),
                    "status": asset["status"],
                    "external_id": asset["externalId"],
                    "metadata": asset["jsonMetadata"],
                    "labels": [
                        {
                            "author": latest_label["author"]["email"],
                            "created_at": latest_label["createdAt"],
                            "label_type": latest_label["labelType"],
                            "label": _format_json_response(
                                jobs_config, latest_label["jsonResponse"]
                            ),
                        }
                    ],
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


def _format_raw_data(asset) -> List[Dict]:
    raw_data = []

    chat_id = asset["jsonMetadata"].get("chat_id", None)

    if (
        "chat_item_ids" in asset["jsonMetadata"]
        and isinstance(asset["jsonMetadata"]["chat_item_ids"], str)
        and len(asset["jsonMetadata"]["chat_item_ids"]) > 0
    ):
        chat_items_ids = str.split(asset["jsonMetadata"]["chat_item_ids"], "_")
    else:
        chat_items_ids = []

    if (
        "models" in asset["jsonMetadata"]
        and isinstance(asset["jsonMetadata"]["models"], str)
        and len(asset["jsonMetadata"]["models"]) > 0
    ):
        models = str.split(asset["jsonMetadata"]["models"], "_")
    else:
        models = []

    with Path(asset["content"]).open(encoding="utf8") as file:
        data = json.load(file)
    version = data.get("version", None)
    if version == "0.1":
        for index, prompt in enumerate(data["prompts"]):
            raw_data.append(
                {
                    "role": prompt.get("title", "user"),
                    "content": prompt["prompt"],
                    "id": _safe_pop(chat_items_ids),
                    "chat_id": chat_id,
                    "model": None,
                }
            )
            raw_data.extend(
                {
                    "role": completion.get("title", "assistant"),
                    "content": completion["content"],
                    "id": _safe_pop(chat_items_ids),
                    "chat_id": chat_id,
                    "model": _safe_pop(models) if index == len(data["prompts"]) - 1 else None,
                }
                for completion in prompt["completions"]
            )
    else:
        raise ValueError(f"Version {version} not supported")
    return raw_data


def _safe_pop(lst, index=0):
    try:
        return lst.pop(index)
    except IndexError:
        return None
