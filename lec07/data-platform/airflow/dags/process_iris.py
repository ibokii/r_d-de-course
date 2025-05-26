from datetime import datetime, timedelta
from typing import Any

import requests

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.utils.context import Context

from python_scripts.train_model import process_iris_data
from dbt_operator import DbtOperator


default_args: dict[str, Any] = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["you@example.com"],
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="process_iris",
    default_args=default_args,
    start_date=datetime(2025, 4, 22),
    end_date=datetime(2025, 4, 24),
    schedule_interval="0 1 * * *",
    catchup=True,
    tags=["iris", "ml", "dbt"],
) as dag:

    def call_and_check_201(url: str, **context: Context) -> int:
        execution_date: str = context['ds']
        response: requests.Response = requests.post(f"{url}?date={execution_date}")
        if response.status_code != 201:
            raise AirflowFailException(f"Expected 201, got {response.status_code}")
        return response.status_code

    transform_task: DbtOperator = DbtOperator(
        task_id="transform_iris_dbt",
        command="run",
        profile="homework",
        target="dev",
        project_dir="/opt/airflow/dags/dbt/homework",
        vars={"processing_date": "{{ ds }}"}
    )

    train_task: PythonOperator = PythonOperator(
        task_id="train_model",
        python_callable=process_iris_data,
    )

    notify_task: EmailOperator = EmailOperator(
        task_id="notify_success",
        to="you@example.com",
        subject="Iris DAG Succeeded",
        html_content="""
            <h3>All tasks process_iris DAG tasks succ done.</h3>
            <p>Піди пряника дістань з верхньої полиці.</p>
        """,
    )

    transform_task >> train_task >> notify_task
