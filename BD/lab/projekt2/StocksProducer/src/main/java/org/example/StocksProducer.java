package org.example;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

import java.io.IOException;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Properties;

public class StocksProducer {
    public static void main(String[] args) {

        String inputDir = args[0];
        String kafkaTopic = args[1];
        String bootstrapServers = args[2];

        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        Producer<String, String> producer = new KafkaProducer<>(props);

        Path directoryPath = Paths.get(inputDir);

        try {
            List<Path> filePaths = new ArrayList<>();
            try (DirectoryStream<Path> directoryStream = Files.newDirectoryStream(directoryPath)) {
                for (Path path : directoryStream) {
                    if (Files.isRegularFile(path)) {
                        filePaths.add(path);
                    }
                }
            }

            Collections.sort(filePaths);

            for (Path path : filePaths) {
                Files.lines(path)
                     .skip(1)
                     .forEach(line -> producer.send(new ProducerRecord<>(kafkaTopic, line)));
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            producer.close();
        }
    }
}