source ./env.sh
spark-submit \
 --conf "spark.driver.extraJavaOptions=${LOG4J_SETTING}" \
 --conf "spark.executor.extraJavaOptions=${LOG4J_SETTING}" \
 --files "${HOME}/log4j.properties" \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 \
 --driver-class-path postgresql-42.6.0.jar \
 --jars postgresql-42.6.0.jar \
 processing.py \
 $SYMBOLS_META \
 $KAFKA_BOOTSTRAP_SERVERS \
 $CHECKPOINTS_LOCATION \
 $KAFKA_DATA_TOPIC \
 $KAFKA_ANOMALY_TOPIC \
 $PG_USER \
 $PGPASSWORD \
 $DB_NAME \
 $DB_TABLE \
 $PROCESSING_MODE \
 $ANOMALIES_WINDOW_SIZE \
 $ANOMALIES_THRESHOLD
