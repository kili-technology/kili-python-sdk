"""Service for exporting kili objects."""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

from typing_extensions import get_args

from kili.domain.asset import AssetId
from kili.domain.project import ProjectId
from kili.services.export.format.base import AbstractExporter, ExportParams
from kili.services.export.format.coco import CocoExporter
from kili.services.export.format.geojson import GeoJsonExporter
from kili.services.export.format.kili import KiliExporter
from kili.services.export.format.llm import LLMExporter
from kili.services.export.format.voc import VocExporter
from kili.services.export.format.yolo import YoloExporter
from kili.services.export.logger import get_logger
from kili.services.export.repository import SDKContentRepository
from kili.services.export.types import CocoAnnotationModifier, ExportType, LabelFormat, SplitOption
from kili.services.types import LogLevel

if TYPE_CHECKING:
    from kili.client import Kili


def export_labels(  # pylint: disable=too-many-arguments, too-many-locals
    kili: "Kili",
    asset_ids: Optional[List[AssetId]],
    project_id: ProjectId,
    export_type: ExportType,
    label_format: LabelFormat,
    split_option: SplitOption,
    single_file: bool,
    output_file: Optional[str],
    disable_tqdm: Optional[bool],
    log_level: LogLevel,
    with_assets: bool,
    annotation_modifier: Optional[CocoAnnotationModifier],
    asset_filter_kwargs: Optional[Dict[str, object]],
    normalized_coordinates: Optional[bool],
    label_type_in: Optional[List[str]],
    include_sent_back_labels: Optional[bool],
) -> Optional[List[Dict[str, Union[List[str], str]]]]:
    """Export the selected assets into the required format, and save it into a file archive."""
    kili.kili_api_gateway.get_project(project_id, ["id"])

    include_sent_back_labels = (
        include_sent_back_labels
        if include_sent_back_labels is not None
        else (label_format != "llm_v1")
    )

    export_params = ExportParams(
        assets_ids=asset_ids,
        project_id=project_id,
        export_type=export_type,
        label_format=label_format,
        split_option=split_option,
        single_file=single_file,
        output_file=Path(output_file) if output_file is not None else None,
        with_assets=with_assets,
        annotation_modifier=annotation_modifier,
        asset_filter_kwargs=asset_filter_kwargs,
        normalized_coordinates=normalized_coordinates,
        label_type_in=label_type_in,
        include_sent_back_labels=include_sent_back_labels,
    )

    logger = get_logger(log_level)

    content_repository = SDKContentRepository(kili.api_endpoint, http_client=kili.http_client)

    if label_format in get_args(LabelFormat):
        format_exporter_selector_mapping: Dict[str, Type[AbstractExporter]] = {
            "raw": KiliExporter,
            "kili": KiliExporter,
            "coco": CocoExporter,
            "yolo_v4": YoloExporter,
            "yolo_v5": YoloExporter,
            "yolo_v7": YoloExporter,
            "yolo_v8": YoloExporter,
            "pascal_voc": VocExporter,
            "geojson": GeoJsonExporter,
            "llm_v1": LLMExporter,
            "llm_dynamic_v1": LLMExporter,
        }
        assert set(format_exporter_selector_mapping.keys()) == set(
            get_args(LabelFormat)
        )  # ensures full mapping
        exporter_class = format_exporter_selector_mapping[label_format]
        return exporter_class(
            export_params, kili, logger, disable_tqdm, content_repository
        ).export_project()

    raise ValueError(f'Label format "{label_format}" is not implemented or does not exist.')
