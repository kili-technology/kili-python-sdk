"""Common code for the Kili exporter."""

import json
from pathlib import Path
from typing import Dict, List

from kili_formats import clean_json_response, convert_to_pixel_coords
from kili_formats.media.video import cut_video
from kili_formats.types import Job, ProjectDict

from kili.services.export.format.base import AbstractExporter


class KiliExporter(AbstractExporter):
    """Common code for Kili exporters."""

    project: ProjectDict  # Ensure self.project is typed as ProjectDict

    ASSETS_DIR_NAME = "assets"

    def _check_arguments_compatibility(self) -> None:
        """Check if the export label format is compatible with the export options."""

    def _check_project_compatibility(self) -> None:
        """Check if the export label format is compatible with the project."""

    def _is_job_compatible(self, job: Job) -> bool:
        """Check if the export label format is compatible with the job."""
        _ = job
        return True  # kili format is compatible with all jobs

    def _save_assets_export(self, assets: List[Dict], output_filename: Path) -> None:
        """Save the assets to a file and return the link to that file."""
        self.logger.info("Exporting to kili format...")

        if self.with_assets:
            if self.project["inputType"] == "VIDEO":
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
                file_path = labels_folder / f"{external_id}.json"
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with file_path.open("wb") as output_file:
                    output_file.write(asset_json.encode("utf-8"))

        self.create_readme_kili_file(self.export_root_folder)

        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _clean_filepaths(self, assets: List[Dict]) -> List[Dict]:
        """Remove TemporaryDirectory() prefix from filepaths in "jsonContent" and "content" fields."""
        for asset in assets:
            if Path(asset["content"]).is_file():
                asset["content"] = str(Path(self.ASSETS_DIR_NAME) / Path(asset["content"]).name)

            json_content_list = []
            if isinstance(asset["jsonContent"], list) and not any(
                isinstance(path, dict) for path in asset["jsonContent"]
            ):
                json_content_list = [
                    str(Path(self.ASSETS_DIR_NAME) / Path(filepath).name)
                    for filepath in asset["jsonContent"]
                    if Path(filepath).is_file()
                ]

                asset["jsonContent"] = json_content_list
        return assets

    def _cut_video_assets(self, assets: List[Dict]) -> List[Dict]:
        """Cut video assets into frames."""
        for asset in assets:
            if asset["jsonContent"] == "" and Path(asset["content"]).is_file():
                nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
                if nbr_frames == 0:
                    continue
                leading_zeros = len(str(nbr_frames))
                try:
                    asset["jsonContent"] = cut_video(
                        video_path=asset["content"],
                        asset=asset,
                        leading_zeros=leading_zeros,
                        output_dir=self.images_folder,
                    )
                except ImportError as e:
                    raise ImportError(
                        "Install with `pip install kili[video]` to use this feature."
                    ) from e
        return assets

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """Extract formatted annotations from labels and save the json in the buckets."""
        clean_assets = self.preprocess_assets(assets)
        if self.project["inputType"] in ["IMAGE", "PDF", "VIDEO"]:
            for i, asset in enumerate(clean_assets):
                clean_assets[i] = convert_to_pixel_coords(asset, self.project)
                clean_json_response(asset)
                if asset is not None:
                    clean_assets[i] = asset
                else:
                    self.logger.warning(
                        "Asset could not be cleaned and was skipped", extra={"asset_index": i}
                    )
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    @property
    def images_folder(self) -> Path:
        """Export images folder."""
        return self.base_folder / self.ASSETS_DIR_NAME
