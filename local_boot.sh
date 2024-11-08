#!/bin/sh
while true; do
    alembic upgrade head
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
exec uvicorn src.main:app --host 0.0.0.0 --port=8011 --reload
