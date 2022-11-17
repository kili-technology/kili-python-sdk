"""
Functions to export a project to Kili format
"""
from typing import Type

from kili.services.export.format.base import ExportParams
from kili.services.export.format.kili.common import KiliExporter

from ..base import BaseExporter, BaseExporterSelector


class KiliExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to Kili
    """

    @staticmethod
    def select_exporter_class(export_params: ExportParams) -> Type[BaseExporter]:
        _ = export_params
        return KiliExporter
