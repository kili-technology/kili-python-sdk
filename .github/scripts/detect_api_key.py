"""Pre-commit to check if api key is present in the code."""

import re
import sys
from pathlib import Path

API_KEY_PATTERN = re.compile(r"(?<!id\":\s\")\b([a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12})\b(?!\.)")

IGNORE = [
    "0005d3cc-3c3f-40b9-93c3-46231c3eb813",  # dicom tag id in recipe
]


def main() -> None:
    args = sys.argv[1:]

    for filepath_str in args:
        filepath = Path(filepath_str)
        assert filepath.exists(), f"{filepath_str} does not exist"

        try:
            content_str = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        search_result = API_KEY_PATTERN.search(content_str)

        if search_result:
            if search_result.group(0) in IGNORE:
                continue

            print(f"API key found in {filepath_str}:  {search_result.group(0)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
