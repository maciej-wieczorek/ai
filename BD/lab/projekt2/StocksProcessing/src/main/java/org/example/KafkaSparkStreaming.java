package org.example;


import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.streaming.StreamingQuery;
import org.apache.spark.sql.streaming.StreamingQueryException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.concurrent.TimeoutException;

public class KafkaSparkStreaming {
    public static String GetHostname() {
        try {
            InetAddress inetAddress = InetAddress.getLocalHost();
            String hostname = inetAddress.getHostName();
            return hostname;
        } catch (UnknownHostException e) {
            System.err.println("Unable to determine the hostname.");
            e.printStackTrace();
            System.exit(1);
        }

        return "";
    }

    public static void main(String[] args) {
        SparkSession spark = SparkSession
                .builder()
                .appName("KafkaSparkStreaming")
                .master("local[*]")
                .getOrCreate();

        // Read from Kafka
        Dataset<Row> df = spark
                .readStream()
                .format("kafka")
                .option("kafka.bootstrap.servers", GetHostname()+":9092")
                .option("subscribe", "kafka-input")
                .load();

        // Select the value column and cast it to string
        Dataset<Row> kafkaData = df.selectExpr("CAST(value AS STRING)");

        // Start the streaming query
        try {
            StreamingQuery query = kafkaData
                    .writeStream()
                    .outputMode("append")
                    .format("console")
                    .start();

            query.awaitTermination();
        } catch (StreamingQueryException | TimeoutException e) {
            e.printStackTrace();
        }
    }
}
