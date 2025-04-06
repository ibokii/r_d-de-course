import os

import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

from config import get_config
from job_raw.bll.exceptions import DataLoadError

# Load and store .env data
load_dotenv()

AUTH_TOKEN: str | None = os.getenv("AUTH_TOKEN")

if not AUTH_TOKEN:
    raise EnvironmentError("AUTH_TOKEN is not set in .env file")


# Get gonfiguration params
config = get_config()

BASE_URL = config["api"]["base_url"]
ENDPOINT = config["api"]["endpoint"]
TIMEOUT = config["api"]["timeout"]


def get_sales(date: str) -> List[Dict[str, Any]]:
    """
    Get all sales data from the API for the specified date.

    :param date: Date to fetch sales data
    :return: List of sales records
    """
    all_sales: List[Dict[str, Any]] = []
    page = 1

    while True:
        params = {
            "date": date,
            "page": page
        }
        headers = {
            "Authorization": AUTH_TOKEN
        }

        url = f"{BASE_URL}{ENDPOINT}"

        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

        if response.status_code == 404:
            break

        if response.status_code != 200:
            raise DataLoadError(f"API request failed: {response.status_code} - {response.text}")

        data = response.json()

        if not data:
            break

        all_sales.extend(data)
        page += 1

    return all_sales
