from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "retries": 0,
}

with DAG(
    dag_id="process_user_profiles",
    default_args=default_args,
    description="ETL for user_profiles JSONLines → Silver",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["user_profiles", "glue", "silver"],
) as dag:

    run_silver = GlueJobOperator(
        task_id="run_user_profiles_silver_etl",
        job_name="process_user_profiles_silver",
        script_location=None,
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        wait_for_completion=True,
        verbose=True,
    )
