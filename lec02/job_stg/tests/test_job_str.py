import os
import json

import pytest
from pathlib import Path
from fastavro import reader

from job_stg.dal.json_loader import read_all_json_files
from job_stg.dal.avro_writer import write_avro


@pytest.fixture
def sample_records():
    return [
        {"client": "Alice", "purchase_date": "2022-08-09", "product": "Laptop", "price": 1200},
        {"client": "Bob", "purchase_date": "2022-08-09", "product": "Fridge", "price": 800}
    ]


def test_read_all_json_files(tmp_path, sample_records):
    # Arrange
    file_1 = tmp_path / "sales_1.json"
    file_2 = tmp_path / "sales_2.json"

    for file in [file_1, file_2]:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(sample_records, f)

    # Act
    result = read_all_json_files(str(tmp_path))

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2 * len(sample_records)
    assert result[0]["client"] == "Alice"


def test_write_avro_creates_file(tmp_path, sample_records):
    # Arrange
    avro_file = tmp_path / "sales_2022-08-09.avro"

    # Act
    write_avro(sample_records, str(avro_file))

    # Assert
    assert avro_file.exists()

    with open(avro_file, "rb") as f:
        records = list(reader(f))

    assert len(records) == len(sample_records)
    assert records[0]["client"] == "Alice"
