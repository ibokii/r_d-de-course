import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window
from awsglue.utils import getResolvedOptions
from pyspark.sql.types import IntegerType, DateType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

df = spark.read.parquet("s3://bokii-data-platform-data-lake-623386377925/bronze/customers/")

window_spec = Window.partitionBy("Id").orderBy(col("RegistrationDate").desc())

df = (
    df.withColumn("rn", row_number().over(window_spec))
      .filter(col("rn") == 1)
      .drop("rn")
)

df = (
    df.withColumnRenamed("Id", "client_id")
      .withColumnRenamed("FirstName", "first_name")
      .withColumnRenamed("LastName", "last_name")
      .withColumnRenamed("Email", "email")
      .withColumnRenamed("RegistrationDate", "registration_date")
      .withColumnRenamed("State", "state")
      .withColumn("client_id", col("client_id").cast(IntegerType()))
      .withColumn("registration_date", col("registration_date").cast(DateType()))
)

df = df.repartition(1)

(
    df.write
    .mode("overwrite")
    .parquet("s3://bokii-data-platform-data-lake-623386377925/silver/customers/")
)
