"""
Functions to export a project to Kili format
"""
from typing import Type

from kili.services.export.format.kili.common import KiliExporter
from kili.services.export.types import SplitOption

from ..base import BaseExporter, BaseExporterSelector


class KiliExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to Kili
    """

    @staticmethod
    def select_exporter_class(split_param: SplitOption) -> Type[BaseExporter]:
        return KiliExporter
