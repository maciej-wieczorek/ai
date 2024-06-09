import sys
import socket
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, min, max, sum, col, split, window, to_json, struct, concat
from pyspark.sql.types import StringType, DoubleType, LongType, TimestampType

if len(sys.argv) != 13:
    print(f"Usage: {sys.argv[0]} <symbols_meta> <bootstrap_servers> <checkpoints_location> <kafka_data_topic> <kafka_anomalies_topic> <db_user> <db_password> <db_name> <db_table> <working_mode> <anomalies_window_size> <anomalies_threshold>")
    raise Exception

symbols_meta = sys.argv[1]
bootstrap_servers = sys.argv[2]
checkpoints_location = sys.argv[3]
kafka_data_topic = sys.argv[4]
kafka_anomalies_topic = sys.argv[5]
db_user = sys.argv[6]
db_password = sys.argv[7]
db_name = sys.argv[8]
db_table = sys.argv[9]
working_mode = sys.argv[10]
anomalies_window_size = sys.argv[11]
anomalies_threshold = int(sys.argv[12])

host_name = socket.gethostname()

spark = SparkSession.builder.appName("Stocks data processing application").getOrCreate()

# źródło danych strumieniowych
lines = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", bootstrap_servers) \
    .option("subscribe", kafka_data_topic) \
    .option("startingOffsets", "latest") \
    .load()

# parsowanie danych oddzielonych przecinkiem i castowanie do typów
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
    ) \
    .dropna().withWatermark("timestamp", "1 days") # usuwamy puste wiersze i dodajemy watermark na opóźnione dane o max 1 dzień

# źródło danych statycznych (informacje o symbolach)
company_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(symbols_meta) \
    .select(col("Symbol").alias("stock"), col("Security Name").alias("company_name"))

# złączenie stream-static
joined_df = parsed_df.join(company_df, "stock", "inner")

# transformacje agregujące
aggregated_df = joined_df \
.groupBy(
    window(col("timestamp"), "30 days"), # grupowanie z wykorzystaniem okna
    col("stock"),
    col("company_name")
).agg(
    avg(col("close")).alias("avg_close"),
    min(col("low")).alias("min_low"),
    max(col("high")).alias("max_high"),
    sum(col("volume")).alias("total_volume")
).select(
    col("window").start.alias("window_start"),
    col("window").end.alias("window_end"),
    col("stock"),
    col("company_name"),
    col("avg_close"),
    col("min_low"),
    col("max_high"),
    col("total_volume")
)

# zapis agregacji do bazy danych
aggregated_query = aggregated_df.writeStream \
    .outputMode(working_mode) \
    .foreachBatch( 
        lambda batchDF, batchId: 
            batchDF.write  
                .format("jdbc")  
                .mode("append")
                .option("url", f"jdbc:postgresql://{host_name}:8432/{db_name}") 
                .option("dbtable", db_table) 
                .option("user", db_user) 
                .option("password", db_password) 
                .save()
    ) \
    .option("checkpointLocation", f"{checkpoints_location}/aggregated") \
    .start()

# anomalie
anomalies_df = joined_df \
.groupBy(
    window(col("timestamp"), f"{anomalies_window_size} days", "1 day"),
    col("stock"),
    col("company_name")
).agg(
    min(col("low")).alias("min_low"),
    max(col("high")).alias("max_high"),
).select (
    col("window"),
    col("stock"),
    col("company_name"),
    col("min_low"),
    col("max_high"),
    (col("max_high") / col("min_low")).alias("high-to-low")
).filter(
    col("high-to-low") >= 1 + (anomalies_threshold / 100)
).select(
    concat(col("stock"), col("window").cast(StringType())).alias("key"), to_json(struct(col("*"))).alias("value")
)

# wypisywanie anomali do tematu kafki
anomalies_query = anomalies_df.writeStream \
    .outputMode(working_mode) \
    .format("kafka") \
    .option("kafka.bootstrap.servers", bootstrap_servers) \
    .option("topic", kafka_anomalies_topic) \
    .option("checkpointLocation", f"{checkpoints_location}/anomalies") \
    .start()

spark.streams.awaitAnyTermination()
