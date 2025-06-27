import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col
from awsglue.utils import getResolvedOptions
from pyspark.sql.types import StructType, StructField, StringType, DateType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

schema = StructType([
    StructField("email", StringType(), True),
    StructField("full_name", StringType(), True),
    StructField("state", StringType(), True),
    StructField("birth_date", StringType(), True),
    StructField("phone_number", StringType(), True),
])

df = (
    spark.read
    .schema(schema)
    .json("s3://bokii-data-platform-data-lake-623386377925/raw/user_profiles/")
)

df = (
    df.withColumn("birth_date", col("birth_date").cast(DateType()))
)

df = df.repartition(1)

(
    df.write
    .mode("overwrite")
    .parquet("s3://bokii-data-platform-data-lake-623386377925/silver/user_profiles/")
)
