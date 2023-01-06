"""
label import service
"""

from pathlib import Path
from typing import Dict, List, Optional, Type, cast

from kili.exceptions import NotFound
from kili.services.helpers import is_target_job_in_json_interface
from kili.services.label_import.importer import (
    AbstractLabelImporter,
    KiliRawLabelImporter,
    LoggerParams,
    YoloLabelImporter,
)
from kili.services.label_import.types import LabelFormat, _ClientInputLabelsValidator
from kili.services.types import LabelType, LogLevel, ProjectId


def import_labels_from_files(  # pylint: disable=too-many-arguments
    kili,
    labels_files: List[str],
    meta_file_path: Optional[str],
    project_id: str,
    input_format: str,
    target_job_name: Optional[str],
    disable_tqdm: bool,
    log_level: str,
    model_name: Optional[str],
    is_prediction: bool,
) -> None:
    """
    Imports labels from a list of files contained in file path.
    """
    if kili.count_projects(project_id=project_id) == 0:
        raise NotFound(f"project ID: {project_id}")

    if len(labels_files) == 0:
        raise ValueError("You must specify files to upload")

    if is_prediction and model_name is None:
        raise ValueError("If predictions are uploaded, a model name should be specified")

    if target_job_name and not is_target_job_in_json_interface(kili, project_id, target_job_name):
        raise NotFound(
            f"Target job {target_job_name} has not been found in the project JSON interface"
        )

    label_importer_class: Optional[Type[AbstractLabelImporter]] = None
    if input_format in ["yolo_v4", "yolo_v5", "yolo_v7"]:
        label_importer_class = YoloLabelImporter
    elif input_format in ["raw", "kili"]:
        label_importer_class = KiliRawLabelImporter
    else:
        raise NotImplementedError(f"{input_format} import is not implemented yet.")

    logger_params = LoggerParams(disable_tqdm=disable_tqdm, level=cast(LogLevel, log_level))
    label_importer = label_importer_class(kili, logger_params, cast(LabelFormat, input_format))
    label_importer.process_from_files(
        [Path(lf) for lf in labels_files],
        Path(meta_file_path) if meta_file_path is not None else None,
        cast(ProjectId, project_id),
        target_job_name,
        model_name,
        is_prediction,
    )


def import_labels_from_dict(  # pylint: disable=too-many-arguments
    kili,
    project_id: Optional[str],
    labels: List[Dict],
    label_type: LabelType,
    model_name: Optional[str] = None,
    disable_tqdm: bool = False,
) -> List:
    """
    Imports labels from a list of dictionaries
    """
    _ClientInputLabelsValidator(labels=labels)
    if label_type == "PREDICTION" and not model_name:
        raise ValueError("You must provide model_name when uploading predictions")
    logger_params = LoggerParams(disable_tqdm=disable_tqdm, level=cast(LogLevel, "WARNING"))
    label_importer = KiliRawLabelImporter(kili, logger_params, cast(LabelFormat, "kili"))
    return label_importer.process_from_dict(
        labels=labels, project_id=project_id, label_type=label_type, model_name=model_name
    )
