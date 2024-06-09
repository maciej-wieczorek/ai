import socket
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, min, max, sum, year, month, col, split, window, to_csv, to_json, struct, concat
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

host_name = socket.gethostname()

spark = SparkSession.builder.appName("Stocks data processing application").getOrCreate()

lines = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f'{host_name}:9092') \
    .option("subscribe", 'stock-data-topic') \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = lines.selectExpr("cast(value as string) as csv") \
    .withColumn("split_csv", split(col("csv"), ",")) \
    .select(
        col("split_csv").getItem(0).cast(TimestampType()).alias("timestamp"),
        col("split_csv").getItem(1).cast(DoubleType()).alias("open"),
        col("split_csv").getItem(2).cast(DoubleType()).alias("high"),
        col("split_csv").getItem(3).cast(DoubleType()).alias("low"),
        col("split_csv").getItem(4).cast(DoubleType()).alias("close"),
        col("split_csv").getItem(5).cast(DoubleType()).alias("adj_close"),
        col("split_csv").getItem(6).cast(LongType()).alias("volume"),
        col("split_csv").getItem(7).alias("stock")
    )

watermarked_df = parsed_df.withWatermark("timestamp", "1 days")

aggregated_df = watermarked_df \
.groupBy(
    window(col("timestamp"), "30 days"),
    col("stock")
).agg(
    avg(col("close")).alias("avg_close"),
    min(col("low")).alias("min_low"),
    max(col("high")).alias("max_high"),
    sum(col("volume")).alias("total_volume")
)

aggregated_query = aggregated_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .option("numRows", "10") \
    .option("checkpointLocation", "/tmp/checkpoints/aggregated") \
    .start()



anomalies_df = parsed_df \
.groupBy(
    window(col("timestamp"), f"2 days", "1 day"),
    col("stock")
).agg(
    min(col("low")).alias("min_low"),
    max(col("high")).alias("max_high"),
).select (
    col("stock"),
    col("window"),
    col("min_low"),
    col("max_high"),
    (col("max_high") / col("min_low")).alias("high-to-low")
).filter(
    col("high-to-low") >= 1.4
).select(
    concat(col("stock"), col("window").cast(StringType())).alias("key"), to_json(struct(col("*"))).alias("value")
)

anomalies_query = anomalies_df.writeStream \
    .outputMode("update") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f'{host_name}:9092') \
    .option("topic", "stock-data-anomalies-topic") \
    .option("checkpointLocation", "/tmp/checkpoints/anomalies") \
    .start()


# query.awaitTermination()