"""
Common code for the yolo exporter.
"""

import json
import os
from tempfile import TemporaryDirectory
from typing import Dict, List

from kili.services.export.format.base import BaseExporter


class KiliExporter(BaseExporter):
    """
    Common code for Kili exporters.
    """

    def process_and_save(self, assets: List[Dict], output_filename: str):
        """
        Extract formatted annotations from labels and save the json in the buckets.
        """
        clean_assets = _filter_out_autosave_labels(assets)
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    def _save_assets_export(self, assets: List[Dict], output_filename: str):
        """
        Save the assets to a file and return the link to that file
        """
        self.logger.info("Exporting to kili format...")

        with TemporaryDirectory() as root_folder:
            base_folder = os.path.join(root_folder, self.project_id)
            os.makedirs(base_folder)
            project_json = json.dumps(assets, sort_keys=True, indent=4)
            with open(os.path.join(base_folder, "data.json"), "wb") as output_file:
                output_file.write(project_json.encode("utf-8"))
            self.create_readme_kili_file(root_folder)
            self.make_archive(root_folder, output_filename)

        self.logger.warning(output_filename)


def _filter_out_autosave_labels(assets: List[Dict]):
    """
    Removes AUTOSAVE labels from exports

    Parameters
    ----------
    - assets: list of assets
    """
    clean_assets = []
    for asset in assets:
        labels = asset.get("labels", [])
        clean_labels = list(filter(lambda label: label["labelType"] != "AUTOSAVE", labels))
        if clean_labels:
            asset["labels"] = clean_labels
        clean_assets.append(asset)
    return clean_assets
