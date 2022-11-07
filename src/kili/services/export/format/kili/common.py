"""
Common code for the yolo exporter.
"""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from kili.orm import Asset
from kili.services.export.format.base import BaseExporter


class KiliExporter(BaseExporter):
    """
    Common code for Kili exporters.
    """

    def _save_assets_export(self, assets: List[Asset], output_filename: str):
        """
        Save the assets to a file and return the link to that file
        """
        self.logger.info("Exporting to kili format...")

        with TemporaryDirectory() as root_folder:
            base_folder = os.path.join(root_folder, self.project_id)
            os.makedirs(base_folder)
            if self.single_file:
                project_json = json.dumps(assets, sort_keys=True, indent=4)
                with open(os.path.join(base_folder, "data.json"), "wb") as output_file:
                    output_file.write(project_json.encode("utf-8"))
            else:
                labels_folder = os.path.join(base_folder, "labels")
                os.makedirs(labels_folder)
                for asset in assets:
                    external_id = asset["externalId"].replace(" ", "_")
                    asset_json = json.dumps(asset, sort_keys=True, indent=4)
                    with open(
                        os.path.join(labels_folder, f"{external_id}.json"), "wb"
                    ) as output_file:
                        output_file.write(asset_json.encode("utf-8"))
            self.create_readme_kili_file(Path(root_folder))
            self.make_archive(root_folder, output_filename)

        self.logger.warning(output_filename)

    def process_and_save(self, assets: List[Asset], output_filename: str):
        """
        Extract formatted annotations from labels and save the json in the buckets.
        """
        clean_assets = self.process_assets(assets, self.label_format)
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )
