"""
Functions to export a project to YOLOv4, v5 or v7 format
"""

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

    def export_project(
        self,
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ) -> None:
        """
        Export a project to YOLO v4 or v5 format
        """
        logger, assets, content_repository = self.get_logger_assets_and_content_repo(
            kili, export_params, logger_params, content_repository_params
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
