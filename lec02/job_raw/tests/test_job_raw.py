import os
import json

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from job_raw.dal.sales_api import get_sales
from job_raw.dal.local_disk import save_to_disk


@pytest.fixture
def fake_sales_data():
    return [
        {"client": "John Doe", "purchase_date": "2022-08-09", "product": "TV", "price": 499},
        {"client": "Jane Smith", "purchase_date": "2022-08-09", "product": "Phone", "price": 899}
    ]


def test_save_to_disk_creates_file(tmp_path, fake_sales_data):
    # Arrange
    date = "2022-08-09"
    file_path = tmp_path / f"sales_{date}.json"

    # Act
    save_to_disk(fake_sales_data, str(file_path))

    # Assert
    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == fake_sales_data


@patch("job_raw.dal.sales_api.requests.get")
def test_get_sales_makes_multiple_requests(mock_get, fake_sales_data):
    # Arrange
    response_page_1 = MagicMock()
    response_page_1.status_code = 200
    response_page_1.json.return_value = fake_sales_data

    response_page_2 = MagicMock()
    response_page_2.status_code = 404  # page doesn't exist = stop

    mock_get.side_effect = [response_page_1, response_page_2]

    # Act
    result = get_sales("2022-08-09")

    # Assert
    assert isinstance(result, list)
    assert len(result) == len(fake_sales_data)
    mock_get.assert_called()
