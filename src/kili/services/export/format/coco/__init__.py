"""
Functions to export a project to Kili format
"""
from typing import Type

from kili.services.export.format.coco.common import CocoExporter
from kili.services.export.types import SplitOption

from ..base import BaseExporter, BaseExporterSelector


class CocoExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to coco
    """

    @staticmethod
    def select_exporter_class(
        split_param: SplitOption,
    ) -> Type[BaseExporter]:
        """
        Export a project to coco format
        """
        return CocoExporter
