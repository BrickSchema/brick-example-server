#! /usr/bin/env sh
set -e

if [ -z ${ENABLE_SSL+x} ]; then
    ENABLE_SSL=false
fi

if [ -f /app/app/main_dev.py ]; then
    DEFAULT_MODULE_NAME=app.main_dev
elif [ -f /app/main_dev.py ]; then
    DEFAULT_MODULE_NAME=main_dev
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-80}
LOG_LEVEL=${LOG_LEVEL:-info}

# If there's a prestart.sh script in the /app directory, run it before starting
PRE_START_PATH=/app/docker/prestart.sh
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

# Start Uvicorn with live reload
if [ $ENABLE_SSL = true ]; then
    if [ -z ${CERTFILE+x} ]; then
        echo "CERTFILE is not defined";
        exit 1
    fi
    if [ -z ${KEYFILE+x} ]; then
        echo "KEYFILE is not defined";
        exit 1
    fi

    echo "SSL is enabled"
    exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE" --ssl-keyfile $KEYFILE  --ssl-certfile $CERTFILE
else
    echo "SSL is disabled"
    exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"
fi
