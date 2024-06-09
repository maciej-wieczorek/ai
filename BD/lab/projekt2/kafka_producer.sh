source ./env.sh

java -jar StocksProducer.jar $INPUT_DIR $KAFKA_DATA_TOPIC $KAFKA_BOOTSTRAP_SERVERS
