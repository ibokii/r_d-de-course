from pathlib import Path
from job_stg.dal.json_loader import read_all_json_files
from job_stg.dal.avro_writer import write_avro


def save_json_as_avro(raw_dir: str, stg_dir: str) -> None:
    """
    Business logic: load sales data from JSON files and save it as Avro.

    :param raw_dir: Path to the directory with raw JSON files
    :param stg_dir: Path to the target directory for Avro file
    """
    records = read_all_json_files(raw_dir)

    if not records:
        raise ValueError(f"No JSON records found in directory: {raw_dir}")

    raw_path = Path(raw_dir)
    date_part = raw_path.name

    avro_file_path = Path(stg_dir) / f"sales_{date_part}.avro"

    write_avro(records, str(avro_file_path))
