import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.sql.types import StructType, StructField, StringType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

schema = StructType([
    StructField("Id", StringType(), True),
    StructField("FirstName", StringType(), True),
    StructField("LastName", StringType(), True),
    StructField("Email", StringType(), True),
    StructField("RegistrationDate", StringType(), True),
    StructField("State", StringType(), True),
])

df = (
    spark.read
    .option("header", True)
    .option("recursiveFileLookup", "true")
    .schema(schema)
    .csv("s3://bokii-data-platform-data-lake-623386377925/raw/customers/")
)

df = df.repartition(1)

(
    df.write
    .mode("overwrite")
    .parquet("s3://bokii-data-platform-data-lake-623386377925/bronze/customers/")
)
