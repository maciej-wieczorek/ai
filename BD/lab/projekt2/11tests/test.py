# pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 --driver-class-path postgresql-42.6.0.jar --jars postgresql-42.6.0.jar

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split, desc
import socket
host_name = socket.gethostname()

spark = SparkSession.builder.appName("KafkaExample").getOrCreate()
lines = spark.readStream.format("kafka").option("kafka.bootstrap.servers", f'{host_name}:9092').option("subscribe", 'kafka-input').load()

words = lines.select(explode(split(lines.value, ",")).alias("word"))
wordCounts = words.groupBy("word").count().orderBy(desc("count"))

query = wordCounts.writeStream.outputMode("complete").format("console").start()
query.awaitTermination()
