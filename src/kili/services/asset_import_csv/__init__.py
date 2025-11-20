"""Method to import assets from a csv file."""

import csv


def get_text_assets_from_csv(from_csv: str, csv_separator: str) -> tuple[list[str], list[str]]:
    """Get text assets from a csv file."""
    content_array: list[str] = []
    external_id_array: list[str] = []

    with open(from_csv, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=csv_separator)

        for row in reader:
            content_array.append(row["content"])
            external_id_array.append(row["externalId"])

    return content_array, external_id_array
