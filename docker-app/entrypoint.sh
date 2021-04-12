#!/bin/sh

mkdir "pgdata"

echo "Waiting for postgres..."

while ! nc -z $DJANGO_DATABASE_HOST $DJANGO_DATABASE_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py migrate
python manage.py collectstatic --no-input --clear

exec "$@"