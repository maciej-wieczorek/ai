export CLUSTER_NAME=$(/usr/share/google/get_metadata_value attributes/dataproc-cluster-name)
export LOG4J_SETTING="-Dlog4j.configuration=file:${HOME}/log4j.properties"
export INPUT_DIR="${HOME}/stocks_result"
export SYMBOLS_META="symbols_valid_meta.csv"
export SYMBOLS_META_PATH="${HOME}/${SYMBOLS_META}"
export KAFKA_DATA_TOPIC="stock-data-topic"
export KAFKA_ANOMALY_TOPIC="stock-data-anomalies-topic"
export KAFKA_BOOTSTRAP_SERVERS="${CLUSTER_NAME}-m:9092"
export PG_USER="postgres"
export PGPASSWORD="mysecretpassword"
export DB_NAME="streamoutput"
export DB_TABLE="stocks_query_output"
export CHECKPOINTS_LOCATION="/tmp/checkpoints"
source ./params.sh
