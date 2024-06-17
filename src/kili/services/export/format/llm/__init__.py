"""Common code for the yolo exporter."""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Union

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
        self.logger.info("Exporting to kili format...")

        if self.single_file:
            project_json = json.dumps(assets, sort_keys=True, indent=4)
            self.base_folder.mkdir(parents=True, exist_ok=True)
            with (self.base_folder / "data.json").open("wb") as output_file:
                output_file.write(project_json.encode("utf-8"))
        else:
            labels_folder = self.base_folder / "labels"
            labels_folder.mkdir(parents=True, exist_ok=True)
            for asset in assets:
                external_id = asset["external_id"].replace(" ", "_")
                asset_json = json.dumps(asset, sort_keys=True, indent=4)
                file_path = labels_folder / f"{external_id}.json"
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with file_path.open("wb") as output_file:
                    output_file.write(asset_json.encode("utf-8"))

        self.create_readme_kili_file(self.export_root_folder)
        shutil.rmtree(self.export_root_folder / self.images_folder)

        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """LLM specific process and save."""
        result = []
        for asset in assets:
            jobs_config = self.project["jsonInterface"]["jobs"]
            json_response = asset["latestLabel"]["jsonResponse"]
            result.append(
                {
                    "raw_data": _format_raw_data(asset),
                    "status": asset["status"],
                    "external_id": asset["externalId"],
                    "metadata": asset["jsonMetadata"],
                    "labels": [_format_json_response(jobs_config, json_response)],
                }
            )

        self._save_assets_export(result, output_filename)


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
                    "role": prompt.get("title", None),
                    "content": prompt["prompt"],
                    "id": _safe_pop(chat_items_ids),
                    "chat_id": chat_id,
                    "model": None,
                }
            )
            raw_data.extend(
                {
                    "role": completion.get("title", None),
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
