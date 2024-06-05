CLUSTER_NAME=$(/usr/share/google/get_metadata_value attributes/dataproc-cluster-name)
kafka-topics.sh --create --bootstrap-server ${CLUSTER_NAME}-m:9092 --replication-factor 2 --partitions 3 --topic kafka-input

# kafka-topics.sh --bootstrap-server ${CLUSTER_NAME}-w-0:9092 --list

sudo cp /usr/lib/kafka/config/tools-log4j.properties /usr/lib/kafka/config/connect-log4j.properties

echo "log4j.logger.org.reflections=ERROR" | sudo tee -a /usr/lib/kafka/config/connect-log4j.properties
