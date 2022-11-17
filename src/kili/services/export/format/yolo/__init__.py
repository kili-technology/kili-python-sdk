"""
Functions to export a project to YOLOv4, v5 or v7 format
"""
from typing import Type

from kili.services.export.format.base import ExportParams

from ..base import BaseExporter, BaseExporterSelector
from .merge import YoloMergeExporter
from .split import YoloSplitExporter


class YoloExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to YOLOv4, v5 or v7
    """

    @staticmethod
    def select_exporter_class(
        export_params: ExportParams,
    ) -> Type[BaseExporter]:
        """
        Export a project to YOLO v4 or v5 format
        """
        if export_params.split_option == "split":
            return YoloSplitExporter
        return YoloMergeExporter
