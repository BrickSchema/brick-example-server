#!/bin/bash

if [ "${POSTGRES_DB:-postgres}" != 'postgres' ]; then
    psql -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c "CREATE EXTENSION IF NOT EXISTS postgis CASCADE;"
fi
