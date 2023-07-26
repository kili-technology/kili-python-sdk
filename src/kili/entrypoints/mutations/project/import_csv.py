"""Import from csv module."""
import csv
import logging
from typing import Dict, List, Optional, Tuple

from kili.services.types import LabelType

logging.basicConfig()
logger = logging.getLogger("kili.entrypoints.mutations.project.import_csv")
logger.setLevel(logging.INFO)


# pylint: disable=too-many-arguments,too-many-locals
def import_text_assets_labels_from_csv(
    kili,
    csv_file: str,
    content_column: str,
    unique_categories: Optional[List[str]],
    category_column: Optional[str],
    external_id_column: Optional[str],
    csv_separator: str,
    label_type: LabelType,
    project_id: Optional[str],
    project_title: Optional[str],
    project_description: Optional[str],
) -> str:
    """Import a csv file into a text classification project."""
    logger.info(f"Reading csv file: {csv_file}")
    content_array, categories_array, external_id_array = _read_csv(
        csv_file, content_column, category_column, external_id_column, csv_separator
    )

    if project_id is None:
        if project_title is None:
            raise ValueError("`project_title` is required if `project_id` is not provided.")

        if project_description is None:
            raise ValueError("`project_description` is required if `project_id` is not provided.")

        if unique_categories:
            categories = unique_categories
        elif categories_array:
            categories = list(set(categories_array))
        else:
            raise ValueError(
                "Cannot create the project if categories are not provided. You must provide either"
                " `unique_categories` or `category_column`."
            )

        project_id = _create_project(kili, project_title, project_description, categories)

        logger.info(f"Created classification project {project_title} with id {project_id}")

    logger.info(f"Adding {len(content_array)} assets to project {project_id}")
    kili.append_many_to_dataset(
        project_id=project_id,
        content_array=content_array,
        external_id_array=external_id_array,
        wait_until_availability=True,
    )

    if category_column is None:
        return project_id

    assert categories_array is not None, categories_array

    logger.info("Adding labels to project.")
    json_response_array = _get_json_response_array(categories_array)
    kili.append_labels(
        json_response_array=json_response_array,
        project_id=project_id,
        asset_external_id_array=external_id_array,
        label_type=label_type,
    )

    return project_id


def _read_csv(
    csv_file: str,
    content_column: str,
    category_column: Optional[str],
    external_id_column: Optional[str],
    csv_separator: str,
) -> Tuple[List[str], Optional[List[str]], List[str]]:
    content_array: List[str] = []
    categories_array: Optional[List[str]] = [] if category_column is not None else None
    external_id_array: List[str] = []

    with open(csv_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=csv_separator)

        for i, row in enumerate(reader):
            content_array.append(row[content_column])

            if category_column is not None and categories_array is not None:
                categories_array.append(row[category_column])

            external_id_array.append(
                row[external_id_column] if external_id_column is not None else str(i + 1)
            )

    return content_array, categories_array, external_id_array


def _create_project(kili, title: str, description: str, categories: List[str]) -> str:
    categories_dict = {
        class_name: {"name": class_name, "children": []}
        for class_name in sorted(categories)
        if isinstance(class_name, str) and class_name
    }
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
                "content": {"categories": categories_dict, "input": "radio"},
                "instruction": "Classification job",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            }
        }
    }
    project_id = kili.create_project(
        input_type="TEXT",
        json_interface=json_interface,
        title=title,
        description=description,
    )["id"]
    return project_id


def _get_json_response_array(categories_array: List[str]) -> List[Dict]:
    json_response_array = []
    for category in categories_array:
        json_resp = (
            {"CLASSIFICATION_JOB": {"categories": [{"name": category}]}}
            if isinstance(category, str) and category
            else {}
        )
        json_response_array.append(json_resp)
    return json_response_array
