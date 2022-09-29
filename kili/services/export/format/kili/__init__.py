"""
Functions to export a project to YOLOv4, v5 or v7 format
"""

from ...repository import SDKContentRepository
from ...tools import fetch_assets
from ..base import (
    BaseExporterSelector,
    ContentRepositoryParams,
    ExportParams,
    LoggerParams,
)
from .common import KiliExporter


class KiliExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to Kili
    """

    @staticmethod
    def export_project(
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ) -> None:
        """
        Export a project to Kili format
        """
        logger = BaseExporterSelector.get_logger(logger_params.level)

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

        return KiliExporter(
            export_params.project_id,
            export_params.export_type,
            export_params.label_format,
            logger_params.disable_tqdm,
            kili,
            logger,
            content_repository,
        ).process_and_save(assets, export_params.output_file)
