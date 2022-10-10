"""
Handles the Yolo export with the split layout
"""

import os
from tempfile import TemporaryDirectory
from typing import Dict, List

from ...exceptions import NoCompatibleJobError
from ...format.yolo.common import YoloExporter, get_category_full_name
from ...types import JobCategory


class YoloSplitExporter(YoloExporter):
    """
    Handles the Yolo format export into split folders
    """

    def process_and_save(self, assets: List[Dict], output_filename: str) -> None:
        self.logger.info("Exporting to yolo format split...")

        json_interface, ml_task, tool = self.get_project_and_init()
        categories_by_job = self._get_categories_by_job(json_interface, ml_task, tool)
        if not categories_by_job:
            raise NoCompatibleJobError(
                f"Error: There is no job in project {self.project_id} "
                f"that can be converted to the {self.label_format} format."
            )

        with TemporaryDirectory() as root_folder:
            images_folder = os.path.join(root_folder, self.project_id, "images")
            os.makedirs(images_folder)
            self._write_jobs_labels_into_split_folders(
                assets,
                categories_by_job,
                root_folder,
                images_folder,
            )
            self.create_readme_kili_file(root_folder)
            self.make_archive(root_folder, output_filename)

        self.logger.warning(output_filename)

    @classmethod
    def _get_categories_by_job(
        cls, json_interface: Dict, ml_task: str, tool: str
    ) -> Dict[str, Dict[str, JobCategory]]:
        """
        Return a dictionary of JobCategory instances by category full name and job id.
        """
        categories_by_job: Dict[str, Dict[str, JobCategory]] = {}
        for job_id, job in json_interface.get("jobs", {}).items():
            if (
                job.get("mlTask") != ml_task
                or tool not in job.get("tools", [])
                or job.get("isModel")
            ):
                continue
            categories: Dict[str, JobCategory] = {}
            for cat_id, category in enumerate(job.get("content", {}).get("categories", {})):
                categories[get_category_full_name(job_id, category)] = JobCategory(
                    category_name=category, id=cat_id, job_id=job_id
                )
            categories_by_job[job_id] = categories
        return categories_by_job

    def _write_jobs_labels_into_split_folders(
        self,
        assets: List[Dict],
        categories_by_job: Dict[str, Dict[str, JobCategory]],
        root_folder: str,
        images_folder: str,
    ) -> None:
        """
        Write assets into split folders.
        """
        for job_id, category_ids in categories_by_job.items():

            base_folder = os.path.join(root_folder, self.project_id, job_id)
            labels_folder = os.path.join(base_folder, "labels")
            os.makedirs(labels_folder)

            self.write_labels_into_single_folder(
                assets,
                category_ids,
                labels_folder,
                images_folder,
                base_folder,
            )
