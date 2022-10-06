"""
label import service
"""

from pathlib import Path
from typing import List, Optional, Type, cast

from kili.exceptions import NotFound
from kili.services.helpers import is_target_job_in_json_interface
from kili.services.label_import.importer import (
    AbstractLabelImporter,
    KiliRawLabelImporter,
    LoggerParams,
    YoloLabelImporter,
)
from kili.services.label_import.types import LabelFormat
from kili.services.types import LogLevel, ProjectId


def import_labels_from_files(  # pylint: disable=too-many-arguments
    kili,
    labels_files_paths_csv: Optional[str],
    labels_files: Optional[List[str]],
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

    if is_prediction and model_name is None:
        raise ValueError("If predictions are uploaded, a model name should be specified")

    if target_job_name and not is_target_job_in_json_interface(kili, project_id, target_job_name):
        raise NotFound(
            f"Target job {target_job_name} has not been found in the project JSON interface"
        )

    label_importer_class: Optional[Type[AbstractLabelImporter]] = None
    if input_format in ["yolo_v4", "yolo_v5", "yolo_v7"]:
        label_importer_class = YoloLabelImporter
    elif input_format == "raw":
        label_importer_class = KiliRawLabelImporter
    else:
        raise NotImplementedError(f"{input_format} import is not implemented yet.")

    logger_params = LoggerParams(disable_tqdm=disable_tqdm, level=cast(LogLevel, log_level))
    label_importer = label_importer_class(kili, logger_params, cast(LabelFormat, input_format))
    label_importer.process_from_files(
        Path(labels_files_paths_csv) if labels_files_paths_csv is not None else None,
        [Path(lf) for lf in labels_files] if labels_files is not None else None,
        Path(meta_file_path) if meta_file_path is not None else None,
        cast(ProjectId, project_id),
        target_job_name,
        model_name,
        is_prediction,
    )
