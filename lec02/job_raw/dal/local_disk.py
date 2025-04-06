import json
import shutil
from typing import List, Dict, Any
from pathlib import Path

from job_raw.bll.exceptions import SaveToDiskError

def save_to_disk(json_content: List[Dict[str, Any]], path: str) -> None:
    """
    Save JSON content to a file. Ensures idempotency by cleaning the directory.

    :param json_content: list of sales records
    :param path: target directory
    :param date: date string for naming the output file
    """
    file_path = Path(path)
    dir_path = file_path.parent

    if dir_path.exists():
        shutil.rmtree(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_content, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise SaveToDiskError(f"Failed to write file: {str(e)}") from e
