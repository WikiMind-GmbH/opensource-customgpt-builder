#!/bin/sh
set -eu

# This runs only on first init (empty volume).
# It can access env vars like POSTGRES_PASSWORD, etc.
: "${CHAT_APP_PASSWORD:?CHAT_APP_PASSWORD is required}"
: "${CGPT_APP_PASSWORD:?CGPT_APP_PASSWORD is required}"

# Create users and databases
psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "chat_context_db" \
  -v chat_pw="$CHAT_APP_PASSWORD" \
  -v cgpt_pw="$CGPT_APP_PASSWORD" <<'SQL'

  CREATE ROLE chat_context_app LOGIN PASSWORD :'chat_pw';
  CREATE ROLE cgpt_context_app LOGIN PASSWORD :'cgpt_pw';

  CREATE DATABASE cgpt_context_db;
SQL
# -v and <<'SQL' to prevent leakage - no problems with special characters like this

# Set up database chat_context_db
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "chat_context_db" <<'SQL'
  REVOKE CONNECT ON DATABASE chat_context_db FROM PUBLIC;
  REVOKE ALL ON SCHEMA public FROM PUBLIC;  
  GRANT CONNECT ON DATABASE chat_context_db TO chat_context_app;
  
  CREATE SCHEMA chat_schema;
  ALTER ROLE chat_context_app SET search_path = chat_schema, pg_catalog;
  GRANT USAGE, CREATE ON SCHEMA chat_schema TO chat_context_app;


SQL
# pg_catalog must be added to guarantee functionality

# Set up database cgpt_context_db
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "cgpt_context_db" <<'SQL'
  REVOKE CONNECT ON DATABASE cgpt_context_db FROM PUBLIC;
  REVOKE ALL ON SCHEMA public FROM PUBLIC;  
  GRANT CONNECT ON DATABASE cgpt_context_db TO cgpt_context_app;
  
  CREATE SCHEMA cgpt_schema;
  ALTER ROLE cgpt_context_app SET search_path = cgpt_schema, pg_catalog;
  GRANT USAGE, CREATE ON SCHEMA cgpt_schema TO cgpt_context_app;
SQL

# FOR MIGRATOR LATER
#   ALTER DEFAULT PRIVILEGES IN SCHEMA chat_schema
#     GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO chat_context_app;