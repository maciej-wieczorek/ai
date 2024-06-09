kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --delete --topic $KAFKA_DATA_TOPIC
kafka-topics.sh --create --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --replication-factor 2 --partitions 3 --topic $KAFKA_DATA_TOPIC
kafka-topics.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --delete --topic $KAFKA_ANOMALY_TOPIC
kafka-topics.sh --create --bootstrap-server $KAFKA_BOOTSTRAP_SERVERS --replication-factor 2 --partitions 3 --topic $KAFKA_ANOMALY_TOPIC
