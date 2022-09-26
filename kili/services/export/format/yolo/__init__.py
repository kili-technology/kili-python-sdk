"""
Functions to export a project to YOLOv4, v5 or v7 format
"""

import logging

from kili.services.types import LogLevel

from ...repository import SDKContentRepository
from ...tools import fetch_assets
from ..base import (
    BaseExporterSelector,
    ContentRepositoryParams,
    ExportParams,
    LoggerParams,
)
from .merge import YoloMergeExporter
from .split import YoloSplitExporter


class YoloExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to YOLOv4, v5 or v7
    """

    @staticmethod
    def export_project(
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ) -> None:
        """
        Export a project to YOLO v4 or v5 format
        """
        logger = YoloExporterSelector.get_logger(logger_params.level)

        logger.info("Fetching assets ...")
        assets = fetch_assets(
            kili,
            project_id=export_params.project_id,
            asset_ids=export_params.assets_ids,
            export_type=export_params.export_type,
            label_type_in=["DEFAULT", "REVIEW"],
            disable_tqdm=logger_params.disable_tqdm,
        )
        content_repository = SDKContentRepository(
            content_repository_params.router_endpoint,
            content_repository_params.router_headers,
            verify_ssl=True,
        )
        if export_params.split_option == "split":

            return YoloSplitExporter(
                export_params.project_id,
                export_params.export_type,
                export_params.label_format,
                logger_params.disable_tqdm,
                kili,
                logger,
                content_repository,
            ).process_and_save(assets, export_params.output_file)

        return YoloMergeExporter(
            export_params.project_id,
            export_params.export_type,
            export_params.label_format,
            logger_params.disable_tqdm,
            kili,
            logger,
            content_repository,
        ).process_and_save(assets, export_params.output_file)

    @staticmethod
    def get_logger(level: LogLevel):
        """Gets the export logger"""
        logger = logging.getLogger("kili.services.export")
        logger.setLevel(level)
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
