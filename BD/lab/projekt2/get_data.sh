source ./env.sh

wget https://www.cs.put.poznan.pl/kjankiewicz/bigdata/stream_project/symbols_valid_meta.csv
hadoop fs -copyFromLocal $SYMBOLS_META_PATH ./
wget https://www.cs.put.poznan.pl/kjankiewicz/bigdata/stream_project/stocks_result.zip
unzip stocks_result.zip
rm stocks_result.zip
