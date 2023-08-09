"""Method to import assets from a csv file."""
import csv
from typing import List, Optional, Tuple


def get_text_assets_from_csv(
    from_csv: str,
    csv_separator: str,
    csv_content_column: Optional[str],
    csv_external_id_column: Optional[str],
    external_id_array: Optional[List[str]],
) -> Tuple[List[str], List[str]]:
    """Get text assets from a csv file."""
    content_array: List[str] = []
    external_id_array_from_csv: List[str] = []

    with open(from_csv, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=csv_separator)

        for i, row in enumerate(reader):
            if csv_content_column is not None:
                content_array.append(row[csv_content_column])
            else:
                content_array.append(next(iter(row.values())))

            external_id_array_from_csv.append(
                row[csv_external_id_column] if csv_external_id_column is not None else str(i + 1)
            )

    return content_array, (
        external_id_array_from_csv if external_id_array is None else external_id_array
    )
