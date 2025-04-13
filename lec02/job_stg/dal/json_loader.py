import json
from typing import List, Dict, Any
from pathlib import Path


def read_all_json_files(raw_dir: str) -> List[Dict[str, Any]]:
    """
    Reads and combines all JSON files in the given directory.

    :param raw_dir: Path to directory with JSON files
    :return: Combined list of records from all files
    """
    records: List[Dict[str, Any]] = []

    raw_path = Path(raw_dir)

    if not raw_path.exists() or not raw_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {raw_dir}")

    for file in raw_path.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records.extend(data)
                else:
                    print(f"⚠️ Skipping non-list JSON file: {file.name}")
        except Exception as e:
            print(f"⚠️ Failed to load {file.name}: {e}")

    return records
