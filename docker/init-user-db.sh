#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE anempty WITH PASSWORD '739154qq';
  CREATE DATABASE kryona;
  ALTER DATABASE kryona OWNER TO anempty;
  GRAND USAGE, CREATE ON SCHEMA public TO anempty;
EOSQL