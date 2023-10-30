"""Label import service."""

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type, cast

from kili.domain.project import ProjectId
from kili.exceptions import NotFound
from kili.services.helpers import is_target_job_in_json_interface
from kili.services.label_import.importer import (
    AbstractLabelImporter,
    KiliRawLabelImporter,
    LoggerParams,
    YoloLabelImporter,
)
from kili.services.label_import.types import LabelFormat
from kili.services.types import LogLevel

if TYPE_CHECKING:
    from kili.client import Kili


def import_labels_from_files(  # pylint: disable=too-many-arguments
    kili: "Kili",
    labels_files: List[str],
    meta_file_path: Optional[str],
    project_id: ProjectId,
    input_format: str,
    target_job_name: Optional[str],
    disable_tqdm: Optional[bool],
    log_level: str,
    model_name: Optional[str],
    is_prediction: bool,
    overwrite: bool,
) -> None:
    """Imports labels from a list of files contained in file path."""
    kili.kili_api_gateway.get_project(project_id, ["id"])

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
        overwrite,
    )
