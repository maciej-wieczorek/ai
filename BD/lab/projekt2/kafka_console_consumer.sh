source ./env.sh

java -jar StocksConsoleConsumer.jar $KAFKA_ANOMALY_TOPIC $KAFKA_BOOTSTRAP_SERVERS
