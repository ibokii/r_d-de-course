from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.utils.dates import days_ago
from datetime import timedelta


BRONZE_JOB_NAME = "process_sales_bronze"
SILVER_JOB_NAME = "process_sales_silver"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="process_sales",
    default_args=default_args,
    description="ETL pipeline: RAW → BRONZE → SILVER",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["sales", "glue", "bronze", "silver"],
) as dag:

    run_bronze = GlueJobOperator(
        task_id="run_bronze_etl",
        job_name=BRONZE_JOB_NAME,
        script_location=None,  
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        wait_for_completion=True,
        verbose=True,
    )

    run_silver = GlueJobOperator(
        task_id="run_silver_etl",
        job_name=SILVER_JOB_NAME,
        aws_conn_id="aws_default",
        region_name="eu-north-1",
        wait_for_completion=True,
        verbose=True,
    )

    run_bronze >> run_silver
