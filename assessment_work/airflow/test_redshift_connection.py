from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

with DAG(
    dag_id="test_redshift_connection",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    test_query = RedshiftDataOperator(
        task_id="test_select_from_external",
        database="dev",
        workgroup_name="bokii-data-platform-workgroup",
        sql="SELECT COUNT(*) FROM silver.silver_customers;",
    )
