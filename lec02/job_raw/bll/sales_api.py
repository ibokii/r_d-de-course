from job_raw.dal.sales_api import get_sales
from job_raw.dal.local_disk import save_to_disk
from pathlib import Path

from job_raw.bll.exceptions import NoSalesDataFound


def save_sales_to_local_disk(date: str, raw_dir: str) -> None:
    """
    Business logic: fetch sales data from API and save it to local disk.

    :param date: Date to fetch sales data
    :param raw_dir: Directory where the file should be saved
    """

    sales_data = get_sales(date)

    if not sales_data:
        raise NoSalesDataFound(f"No sales data found for {date}")

    file_path = Path(raw_dir) / f"sales_{date}.json"


    save_to_disk(sales_data, str(file_path))
