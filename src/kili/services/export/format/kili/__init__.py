"""
Common code for the Kili exporter.
"""

import json
import os
from pathlib import Path
from typing import List

from kili.orm import Asset
from kili.services.export.format.base import AbstractExporter

from ...media.video import cut_video


class KiliExporter(AbstractExporter):
    """
    Common code for Kili exporters.
    """

    ASSETS_DIR_NAME = "assets"

    def _check_arguments_compatibility(self):
        """
        Checks if the export label format is compatible with the export options.
        """

    def _check_project_compatibility(self) -> None:
        """
        Checks if the export label format is compatible with the project.
        """

    def _save_assets_export(self, assets: List[Asset], output_filename: Path):
        """
        Save the assets to a file and return the link to that file
        """
        self.logger.info("Exporting to kili format...")

        if self.with_assets:
            if self.project_input_type == "VIDEO":
                assets = self._cut_video_assets(assets)

            assets = self._clean_filepaths(assets)

        if self.single_file:
            project_json = json.dumps(assets, sort_keys=True, indent=4)
            self.base_folder.mkdir(parents=True, exist_ok=True)
            with (self.base_folder / "data.json").open("wb") as output_file:
                output_file.write(project_json.encode("utf-8"))
        else:
            labels_folder = self.base_folder / "labels"
            labels_folder.mkdir(parents=True, exist_ok=True)
            for asset in assets:
                external_id = asset["externalId"].replace(" ", "_")
                asset_json = json.dumps(asset, sort_keys=True, indent=4)
                with (labels_folder / f"{external_id}.json").open("wb") as output_file:
                    output_file.write(asset_json.encode("utf-8"))

        self.create_readme_kili_file(self.export_root_folder)

        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _clean_filepaths(self, assets: List[Asset]):
        """
        Remove TemporaryDirectory() prefix from filepaths in "jsonContent" and "content" fields.
        """
        for asset in assets:
            if os.path.isfile(asset["content"]):
                asset["content"] = str(Path(self.ASSETS_DIR_NAME) / Path(asset["content"]).name)

            json_content_list = []
            if isinstance(asset["jsonContent"], list):
                for filepath in asset["jsonContent"]:
                    if os.path.isfile(filepath):
                        json_content_list.append(
                            str(Path(self.ASSETS_DIR_NAME) / Path(filepath).name)
                        )
                asset["jsonContent"] = json_content_list
        return assets

    def _cut_video_assets(self, assets: List[Asset]):
        """
        Cut video assets into frames
        """
        for asset in assets:
            if asset["jsonContent"] == "" and os.path.isfile(asset["content"]):
                nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
                if nbr_frames == 0:
                    continue
                leading_zeros = len(str(nbr_frames))
                asset["jsonContent"] = cut_video(
                    video_path=asset["content"],
                    asset=asset,
                    leading_zeros=leading_zeros,
                    output_dir=self.images_folder,
                )
        return assets

    def process_and_save(self, assets: List[Asset], output_filename: Path):
        """
        Extract formatted annotations from labels and save the json in the buckets.
        """
        clean_assets = self.pre_process_assets(assets, self.label_format)
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    @property
    def images_folder(self) -> Path:
        """
        Export images folder
        """
        return self.base_folder / self.ASSETS_DIR_NAME
