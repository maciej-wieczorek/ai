source ./env.sh

sudo rm -rf /tmp/*
hdfs dfs -rm -r $CHECKPOINTS_LOCATION
