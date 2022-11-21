"""Service for exporting kili objects """

from pathlib import Path
from typing import Dict, List, Optional, Type

from typing_extensions import get_args

from kili.exceptions import NotFound
from kili.services.export.format.base import AbstractExporter, ExportParams
from kili.services.export.format.coco import CocoExporter
from kili.services.export.format.kili import KiliExporter
from kili.services.export.format.yolo import YoloExporter
from kili.services.export.logger import get_logger
from kili.services.export.repository import SDKContentRepository
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
        output_file=Path(output_file),
    )

    logger = get_logger(log_level)

    content_repository = SDKContentRepository(
        kili.auth.api_endpoint,
        router_headers={
            "Authorization": f"X-API-Key: {kili.auth.api_key}",
        },
        verify_ssl=True,
    )

    if label_format in get_args(LabelFormat):
        format_exporter_selector_mapping: Dict[str, Type[AbstractExporter]] = {
            "raw": KiliExporter,
            "kili": KiliExporter,
            "coco": CocoExporter,
            "yolo_v4": YoloExporter,
            "yolo_v5": YoloExporter,
            "yolo_v7": YoloExporter,
        }
        assert set(format_exporter_selector_mapping.keys()) == set(
            get_args(LabelFormat)
        )  # ensures full mapping
        exporter_class = format_exporter_selector_mapping[label_format]
        exporter_class(
            export_params, kili, logger, disable_tqdm, content_repository
        ).export_project()
    else:
        raise ValueError(f'Label format "{label_format}" is not implemented or does not exist.')
