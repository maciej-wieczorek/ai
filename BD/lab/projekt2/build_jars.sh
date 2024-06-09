source ./env.sh

sudo apt install maven -y

mvn package -f StocksProducer/pom.xml
cp StocksProducer/target/StocksProducer-1.0-SNAPSHOT.jar ./StocksProducer.jar
mvn package -f StocksConsoleConsumer/pom.xml
cp StocksConsoleConsumer/target/StocksConsoleConsumer-1.0-SNAPSHOT.jar ./StocksConsoleConsumer.jar