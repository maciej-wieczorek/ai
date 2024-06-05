import socket
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, min, max, sum, year, month, col, split
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

# Get the host name
host_name = socket.gethostname()

# Create Spark session
spark = SparkSession.builder.appName("KafkaExample").getOrCreate()

# Read data from Kafka
lines = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", f'{host_name}:9092') \
    .option("subscribe", 'kafka-input') \
    .option("startingOffsets", "earliest") \
    .load()

# Define schema for the data
schema = StructType([
    StructField("Date", TimestampType(), True),
    StructField("Open", DoubleType(), True),
    StructField("High", DoubleType(), True),
    StructField("Low", DoubleType(), True),
    StructField("Close", DoubleType(), True),
    StructField("Adj_Close", DoubleType(), True),
    StructField("Volume", LongType(), True),
    StructField("Stock", StringType(), True)
])

# Parse the CSV data
parsed_df = lines.selectExpr("CAST(value AS STRING) as csv") \
    .select(
        split(col("csv"), ",")[0].alias("Date"),
        split(col("csv"), ",")[1].cast(DoubleType()).alias("Open"),
        split(col("csv"), ",")[2].cast(DoubleType()).alias("High"),
        split(col("csv"), ",")[3].cast(DoubleType()).alias("Low"),
        split(col("csv"), ",")[4].cast(DoubleType()).alias("Close"),
        split(col("csv"), ",")[5].cast(DoubleType()).alias("Adj_Close"),
        split(col("csv"), ",")[6].cast(LongType()).alias("Volume"),
        split(col("csv"), ",")[7].alias("Stock")
    )


# Add year and month columns for aggregation
parsed_df = parsed_df.withColumn("Date", col("Date").cast(TimestampType()))
parsed_df = parsed_df.withColumn("year", year(col("Date"))).withColumn("month", month(col("Date")))

parsed_df.printSchema()


# potrzebne miesięczne okno

# Perform the necessary transformations to get the monthly aggregations
aggregated_df = parsed_df.groupBy(
    col("year"),
    col("month"),
    col("Stock")
).agg(
    avg(col("Close")).alias("avg_close"),
    min(col("Low")).alias("min_low"),
    max(col("High")).alias("max_high"),
    sum(col("Volume")).alias("total_volume")
).select(
    col("year"),
    col("month"),
    col("Stock"),
    col("avg_close"),
    col("min_low"),
    col("max_high"),
    col("total_volume")
)

# Define the output sink (for example, console or Kafka)
query = aggregated_df.writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", "false") \
    .start()

# Wait for the termination of the query
query.awaitTermination()