import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import (
    col, regexp_replace, to_date, trim,
    split, lpad, concat_ws
)
from pyspark.sql.types import DoubleType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

df = spark.read.parquet("s3://bokii-data-platform-data-lake-623386377925/bronze/sales/")

df = df.withColumn(
    "price",
    trim(regexp_replace(col("Price"), r"(USD\s*|\$|,)", "")).cast(DoubleType())
)

df = df.withColumn("PurchaseDate", regexp_replace(col("PurchaseDate"), "/", "-"))

parts = split(col("PurchaseDate"), "-")
year = parts.getItem(0)
month = lpad(parts.getItem(1), 2, "0")
day = lpad(parts.getItem(2), 2, "0")
normalized_date_str = concat_ws("-", year, month, day)

df = df.withColumn("purchase_date", to_date(normalized_date_str, "yyyy-MM-dd"))

df = df.filter(col("purchase_date").isNotNull())

(
    df.select(
        col("CustomerId").alias("customer_id"),
        col("Product").alias("product"),
        col("price"),
        col("purchase_date")
    )
    .write
    .mode("overwrite")
    .partitionBy("purchase_date")
    .parquet("s3://bokii-data-platform-data-lake-623386377925/silver/sales/")
)
