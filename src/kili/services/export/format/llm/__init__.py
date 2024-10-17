"""Common code for the llm exporter."""

import json
import logging
import warnings
from ast import literal_eval
from pathlib import Path
from typing import Dict, List, Optional, Union

from kili.services.asset_import.helpers import SEPARATOR
from kili.services.export.exceptions import NotCompatibleInputType
from kili.services.export.format.base import AbstractExporter
from kili.services.export.format.llm.types import ExportLLMItem, RankingValue
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
        result = self.process(assets)
        self._save_assets_export(result, output_filename)

    def process(self, assets: List[Dict]) -> List[Dict[str, Union[List[str], str]]]:
        """LLM specific process."""
        warnings.warn(
            "Exporting llm labels with `kili.export_labels` is deprecated."
            " Please use `kili.llm.export` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        clean_assets = self.preprocess_assets(assets)
        if self.label_format == "llm_v1":
            return self._process_llm_v1(clean_assets)
        return self._process_llm_dynamic_v1(clean_assets)

    def _process_llm_dynamic_v1(self, assets: List[Dict]) -> List[Dict[str, Union[List[str], str]]]:
        result = []
        for asset in assets:
            step_number = _count_step(asset)
            label = asset["latestLabel"]
            steps = {}
            context = []
            formatted_asset = _format_raw_data(asset, all_model_keys=True)
            for i in range(step_number):
                steps[f"{i}"] = {
                    "raw_data": context + _format_raw_data(asset, i),
                    "status": asset["status"],
                    "external_id": asset["externalId"],
                    "metadata": asset["jsonMetadata"],
                    "labels": [
                        {
                            "author": label["author"]["email"],
                            "created_at": label["createdAt"],
                            "label_type": label["labelType"],
                            "label": _format_json_response_dynamic(
                                self.project["jsonInterface"]["jobs"], label["jsonResponse"], i
                            ),
                        }
                    ],
                }
                next_context = _get_next_step_context(formatted_asset, label["jsonResponse"], i)
                context = context + next_context

            if step_number > 0:
                result.append(steps)
        return result

    def _process_llm_v1(self, assets: List[Dict]) -> List[Dict[str, Union[List[str], str]]]:
        result = []
        if len(assets) == 0:
            return result
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
                                    self.project["jsonInterface"]["jobs"], label["jsonResponse"]
                                ),
                            },
                            asset["labels"],
                        )
                    ),
                }
            )
        return result


def _get_step_ranking_value(json_response: Dict, step_number: int) -> RankingValue:
    prefix = f"STEP_{step_number+1}_"
    for category in json_response["CLASSIFICATION_JOB"]["categories"]:
        if category["name"] != f"STEP_{step_number+1}":
            continue

        for children_name, children_value in category["children"].items():
            if children_name == f"STEP_{step_number+1}_RANKING":
                raw_value = children_value["categories"][0]["name"]
                return raw_value[len(prefix) :]
    return RankingValue.TIE


def _get_next_step_context(
    formatted_asset: List[ExportLLMItem], json_response: Dict, step_number: int
) -> List[ExportLLMItem]:
    context = []
    skipped_context = 0
    completion_index = 0
    ranking = _get_step_ranking_value(json_response, step_number)
    for item in formatted_asset:
        if skipped_context > step_number:
            break

        if skipped_context == step_number:
            if item["role"] == "user":
                context.append(item)
            else:
                if completion_index == 0 and ranking in ["A_1", "A_2", "A_3", "TIE"]:
                    context.append(item)
                    break
                if completion_index == 1 and ranking in ["B_1", "B_2", "B_3"]:
                    context.append(item)
                    break
                completion_index += 1

        if item["role"] == "assistant":
            skipped_context += 1

    return context


def _count_step(asset: Dict) -> int:
    label = asset["latestLabel"]
    if "jsonResponse" not in label and "CLASSIFICATION_JOB" not in label["jsonResponse"]:
        return 0
    return len(label["jsonResponse"]["CLASSIFICATION_JOB"]["categories"])


def _format_json_response_dynamic(
    jobs_config: Dict, json_response: Dict, step_number: int
) -> Dict[str, Union[str, List[str]]]:
    # check subjobs of the step
    job_step = f"STEP_{step_number+1}"
    for item in json_response["CLASSIFICATION_JOB"]["categories"]:
        if item["name"] != job_step:
            continue
        response_step = _format_json_response(jobs_config, item["children"])
        formatted_response = literal_eval(str(response_step).replace(job_step + "_", ""))
        return formatted_response
    return {}


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
