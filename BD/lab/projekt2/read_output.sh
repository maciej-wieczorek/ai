source ./env.sh

psql -h localhost -p 8432 -U $PG_USER -v db_name="$DB_NAME" -v db_table="$DB_TABLE" -f query_database.sql
