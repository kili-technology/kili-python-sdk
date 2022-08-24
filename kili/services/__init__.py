"""
Python SDK service layer
"""
from typing import List, Optional

from typing_extensions import get_args

from kili.services.export.format.base import (
    ContentRepositoryParams,
    ExportParams,
    LoggerParams,
)
from kili.services.export.format.yolo import YoloExporterSelector
from kili.services.export.typing import ExportType, LabelFormat, LogLevel, SplitOption


def export_labels(  # pylint: disable=too-many-arguments
    kili,
    asset_ids: Optional[List[str]],
    project_id: str,
    export_type: ExportType,
    label_format: LabelFormat,
    split_option: SplitOption,
    output_file: str,
    disable_tqdm: bool,
    log_level: LogLevel,
) -> None:
    """
    Export the selected assets into the required format, and save it into a file archive.
    """
    export_params = ExportParams(
        assets_ids=asset_ids,
        project_id=project_id,
        export_type=export_type,
        label_format=label_format,
        split_option=split_option,
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
        YoloExporterSelector.export_project(
            kili, export_params, logger_params, content_repository_params
        )
    else:
        raise ValueError(f'Label format "{label_format}" is not implemented or does not exist.')
