from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

REDSHIFT_CONN_ID = "redshift_default"
SCHEMA_SRC = "silver"
SCHEMA_DST = "gold"
S3_SILVER_CUSTOMERS = "s3://bokii-data-platform-data-lake-623386377925/silver/customers/"
S3_SILVER_USER_PROFILES = "s3://bokii-data-platform-data-lake-623386377925/silver/user_profiles/"
IAM_ROLE_ARN = "arn:aws:iam::623386377925:role/bokii-data-platform-redshift-service-role"
REDSHIFT_DATABASE = "dev"
REDSHIFT_WORKGROUP = "bokii-data-platform-workgroup"

with DAG(
    dag_id="enrich_user_profiles",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["gold", "redshift", "enrichment"],
) as dag:

    create_schemas = RedshiftDataOperator(
        task_id="create_schemas",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        CREATE SCHEMA IF NOT EXISTS {SCHEMA_SRC};
        CREATE SCHEMA IF NOT EXISTS {SCHEMA_DST};
        """,
    )

    create_silver_customers_table = RedshiftDataOperator(
        task_id="create_silver_customers_table",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_SRC}.silver_customers (
            client_id INT,
            first_name VARCHAR,
            last_name VARCHAR,
            email VARCHAR,
            registration_date DATE,
            state VARCHAR
        );
        """,
    )

    create_silver_user_profiles_table = RedshiftDataOperator(
        task_id="create_silver_user_profiles_table",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_SRC}.silver_user_profiles (
            email VARCHAR,
            full_name VARCHAR,
            state VARCHAR,
            birth_date DATE,
            phone_number VARCHAR
        );
        """,
    )

    copy_silver_customers = RedshiftDataOperator(
        task_id="copy_silver_customers",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        DELETE FROM {SCHEMA_SRC}.silver_customers;
        COPY {SCHEMA_SRC}.silver_customers
        FROM '{S3_SILVER_CUSTOMERS}'
        IAM_ROLE '{IAM_ROLE_ARN}'
        FORMAT AS PARQUET;
        """,
    )

    copy_silver_user_profiles = RedshiftDataOperator(
        task_id="copy_silver_user_profiles",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        DELETE FROM {SCHEMA_SRC}.silver_user_profiles;
        COPY {SCHEMA_SRC}.silver_user_profiles
        FROM '{S3_SILVER_USER_PROFILES}'
        IAM_ROLE '{IAM_ROLE_ARN}'
        FORMAT AS PARQUET;
        """,
    )

    create_gold_table = RedshiftDataOperator(
        task_id="create_gold_table",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_DST}.user_profiles_enriched (
            client_id INT,
            first_name VARCHAR,
            last_name VARCHAR,
            email VARCHAR PRIMARY KEY,
            registration_date DATE,
            state VARCHAR,
            birth_date DATE,
            phone_number VARCHAR
        );
        """,
    )

    merge_enriched = RedshiftDataOperator(
        task_id="merge_user_profiles",
        database=REDSHIFT_DATABASE,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        MERGE INTO {SCHEMA_DST}.user_profiles_enriched AS tgt
        USING (
            SELECT
                c.client_id,
                COALESCE(c.first_name, SPLIT_PART(p.full_name, ' ', 1)) AS first_name,
                COALESCE(c.last_name, SPLIT_PART(p.full_name, ' ', 2)) AS last_name,
                c.email,
                c.registration_date,
                COALESCE(c.state, p.state) AS state,
                p.birth_date,
                p.phone_number
            FROM {SCHEMA_SRC}.silver_customers c
            LEFT JOIN {SCHEMA_SRC}.silver_user_profiles p
            ON c.email = p.email
        ) AS src
        ON tgt.email = src.email
        WHEN MATCHED THEN UPDATE SET
            client_id = src.client_id,
            first_name = src.first_name,
            last_name = src.last_name,
            registration_date = src.registration_date,
            state = src.state,
            birth_date = src.birth_date,
            phone_number = src.phone_number
        WHEN NOT MATCHED THEN INSERT (
            client_id, first_name, last_name, email, registration_date, state, birth_date, phone_number
        ) VALUES (
            src.client_id, src.first_name, src.last_name, src.email, src.registration_date,
            src.state, src.birth_date, src.phone_number
        );
        """,
    )

    create_schemas >> create_silver_customers_table >> copy_silver_customers
    create_schemas >> create_silver_user_profiles_table >> copy_silver_user_profiles
    copy_silver_customers >> create_gold_table
    copy_silver_user_profiles >> create_gold_table
    create_gold_table >> merge_enriched
