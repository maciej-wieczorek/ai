source ./env.sh

wget https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
docker run --name postgresdb -p 8432:5432 -e POSTGRES_PASSWORD=$PGPASSWORD -d postgres
sleep 10

source ./db_reset.sh
