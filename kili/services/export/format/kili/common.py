"""
Common code for the yolo exporter.
"""

import json
import os
from tempfile import TemporaryDirectory
from typing import Dict, List

from kili.orm import Label
from kili.services.export.format.base import BaseExporter


class KiliExporter(BaseExporter):
    """
    Common code for Kili exporters.
    """

    def process_and_save(self, assets: List[Dict], output_filename: str):
        """
        Extract formatted annotations from labels and save the json in the buckets.
        """
        clean_assets = _process_assets(assets)
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    def _save_assets_export(self, assets: List[Dict], output_filename: str):
        """
        Save the assets to a file and return the link to that file
        """
        self.logger.info("Exporting to kili format merged...")

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


def _process_assets(assets: List[Dict]):
    """
    Format labels in the requested format, and filter out autosave labels
    """
    assets_in_format = []
    for asset in assets:
        if "labels" in asset:
            labels_of_asset = []
            for label in asset["labels"]:
                clean_label = _format_json_response(label)
                labels_of_asset.append(clean_label)
            asset["labels"] = labels_of_asset
        if "latestLabel" in asset:
            label = asset["latestLabel"]
            if label is not None:
                clean_label = _format_json_response(label)
                asset["latestLabel"] = clean_label
        assets_in_format.append(asset)

    clean_assets = _filter_out_autosave_labels(assets_in_format)
    return clean_assets


def _format_json_response(label: Label):
    """
    Format the label JSON response in the requested format
    """
    formatted_json_response = label.json_response()
    label["jsonResponse"] = formatted_json_response
    return label
