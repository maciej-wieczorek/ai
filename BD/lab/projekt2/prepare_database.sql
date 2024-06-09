drop database if exists :db_name;
create database :db_name;

\c :db_name

create table :db_table (
     id bigserial primary key,
     window_start timestamp not null,
     window_end timestamp not null,
     stock varchar(16) not null,
     company_name varchar(512) not null,
     avg_close decimal not null,
     min_low decimal not null,
     max_high decimal not null,
     total_volume decimal not null
);
