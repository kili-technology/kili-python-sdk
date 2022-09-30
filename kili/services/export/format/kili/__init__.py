"""
Functions to export a project to Kili format
"""

from kili.services.export.format.base import (
    BaseExporterSelector,
    ContentRepositoryParams,
    ExportParams,
    LoggerParams,
)
from kili.services.export.format.kili.common import KiliExporter


class KiliExporterSelector(BaseExporterSelector):
    # pylint: disable=too-few-public-methods

    """
    Formatter to export to Kili
    """

    def export_project(
        self,
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ) -> None:
        """
        Export a project to Kili format
        """
        logger, assets, content_repository = self.get_logger_assets_and_content_repo(
            kili, export_params, logger_params, content_repository_params
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
