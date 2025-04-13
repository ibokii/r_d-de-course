import shutil
from pathlib import Path
from typing import List, Dict, Any
from fastavro import writer, parse_schema


def write_avro(records: List[Dict[str, Any]], file_path: str) -> None:
    """
    Write list of records to an Avro file.

    :param records: List of JSON-like dictionaries
    :param file_path: Full path to output .avro file
    """
    if not records:
        raise ValueError("Cannot write empty records to Avro")

    example_record = records[0]
    schema = {
        "doc": "Sales data",
        "name": "Sale",
        "namespace": "sales.avro",
        "type": "record",
        "fields": [
            {"name": key, "type": ["null", _infer_avro_type(value)]}
            for key, value in example_record.items()
        ]
    }

    parsed_schema = parse_schema(schema)

    file_path_obj = Path(file_path)
    output_dir = file_path_obj.parent

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(file_path_obj, "wb") as out:
        writer(out, parsed_schema, records)


def _infer_avro_type(value: Any) -> str:
    """
    Infer Avro field type based on Python value.
    """
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    else:
        return "string"
