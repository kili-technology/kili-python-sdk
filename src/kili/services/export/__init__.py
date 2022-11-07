"""Service for exporting kili objects """

from typing import List, Optional

from typing_extensions import get_args

from kili.exceptions import NotFound
from kili.services.export.format.base import (
    ContentRepositoryParams,
    ExportParams,
    LoggerParams,
)
from kili.services.export.format.coco import CocoExporterSelector
from kili.services.export.format.kili import KiliExporterSelector
from kili.services.export.format.yolo import YoloExporterSelector
from kili.services.export.types import ExportType, LabelFormat, SplitOption
from kili.services.types import LogLevel, ProjectId


def export_labels(  # pylint: disable=too-many-arguments, too-many-locals
    kili,
    asset_ids: Optional[List[str]],
    project_id: ProjectId,
    export_type: ExportType,
    label_format: LabelFormat,
    split_option: SplitOption,
    single_file: bool,
    output_file: str,
    disable_tqdm: bool,
    log_level: LogLevel,
) -> None:
    """
    Export the selected assets into the required format, and save it into a file archive.
    """
    if kili.count_projects(project_id=project_id) == 0:
        raise NotFound(f"project ID: {project_id}")

    export_params = ExportParams(
        assets_ids=asset_ids,
        project_id=project_id,
        export_type=export_type,
        label_format=label_format,
        split_option=split_option,
        single_file=single_file,
        output_file=output_file,
    )

    logger_params = LoggerParams(
        disable_tqdm=disable_tqdm,
        level=log_level,
    )

    content_repository_params = ContentRepositoryParams(
        router_endpoint=kili.auth.api_endpoint,
        router_headers={
            "Authorization": f"X-API-Key: {kili.auth.api_key}",
        },
    )

    if label_format in get_args(LabelFormat):
        format_exporter_selector_mapping = {
            "raw": KiliExporterSelector,
            "kili": KiliExporterSelector,
            "coco": CocoExporterSelector,
            "yolo_v4": YoloExporterSelector,
            "yolo_v5": YoloExporterSelector,
            "yolo_v7": YoloExporterSelector,
        }
        assert set(format_exporter_selector_mapping.keys()) == set(
            get_args(LabelFormat)
        )  # ensures full mapping
        exporter_selector = format_exporter_selector_mapping[label_format]
        exporter = exporter_selector.init_exporter(
            kili, logger_params, export_params, content_repository_params
        )
        exporter.export_project(kili, export_params, logger_params)
    else:
        raise ValueError(f'Label format "{label_format}" is not implemented or does not exist.')
