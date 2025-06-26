import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.types import StructType, StructField, StringType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

schema = StructType([
    StructField("CustomerId", StringType(), True),
    StructField("PurchaseDate", StringType(), True),
    StructField("Product", StringType(), True),
    StructField("Price", StringType(), True),
])

df = (
    spark.read
    .option("header", True)
    .option("recursiveFileLookup", "true")
    .schema(schema)
    .csv("s3://bokii-data-platform-data-lake-623386377925/raw/sales/")
)

df = df.repartition(1)

(
    df.write
    .mode("overwrite")
    .parquet("s3://bokii-data-platform-data-lake-623386377925/bronze/sales/")
)
