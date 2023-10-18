"""Method to import assets from a csv file."""

import csv
from typing import List, Tuple


def get_text_assets_from_csv(from_csv: str, csv_separator: str) -> Tuple[List[str], List[str]]:
    """Get text assets from a csv file."""
    content_array: List[str] = []
    external_id_array: List[str] = []

    with open(from_csv, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=csv_separator)

        for row in reader:
            content_array.append(row["content"])
            external_id_array.append(row["externalId"])

    return content_array, external_id_array
