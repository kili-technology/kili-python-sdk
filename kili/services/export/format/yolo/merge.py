"""
Functions to export a project to YOLOv4 or v5 format, with a merged folder layout
"""
import os
from tempfile import TemporaryDirectory
from typing import Dict, List

from ...exceptions import NoCompatibleJobError
from ...format.yolo.common import YoloExporter, get_category_full_name
from ...types import JobCategory


class YoloMergeExporter(YoloExporter):
    """
    Handles the Yolo export to merged folders.
    """

    def process_and_save(self, assets: List[Dict], output_filename: str) -> None:
        self.logger.info("Exporting to yolo format merged...")
        json_interface, ml_task, tool = self.get_project_and_init()
        merged_categories_id = self._get_merged_categories(json_interface, ml_task, tool)
        if not merged_categories_id:
            raise NoCompatibleJobError(
                f"Error: There is no job in project {self.project_id} "
                f"that can be converted to the {self.label_format} format."
            )

        with TemporaryDirectory() as root_folder:
            base_folder = os.path.join(root_folder, self.project_id)
            images_folder = os.path.join(base_folder, "images")
            labels_folder = os.path.join(base_folder, "labels")
            os.makedirs(images_folder)
            os.makedirs(labels_folder)
            self.write_labels_into_single_folder(
                assets,
                merged_categories_id,
                labels_folder,
                images_folder,
                base_folder,
            )
            self.create_readme_kili_file(root_folder)
            self.make_archive(root_folder, output_filename)

        self.logger.warning(output_filename)

    @classmethod
    def _get_merged_categories(
        cls, json_interface: Dict, ml_task: str, tool: str
    ) -> Dict[str, JobCategory]:
        """
        Return a dictionary of JobCategory instances by category full name.
        """
        cat_number = 0
        merged_categories_id: Dict[str, JobCategory] = {}
        for job_id, job in json_interface.get("jobs", {}).items():
            if (
                job.get("mlTask") != ml_task
                or tool not in job.get("tools", [])
                or job.get("isModel")
            ):
                continue
            for category in job.get("content", {}).get("categories", {}):
                merged_categories_id[get_category_full_name(job_id, category)] = JobCategory(
                    category_name=category, id=cat_number, job_id=job_id
                )
                cat_number += 1

        return merged_categories_id
