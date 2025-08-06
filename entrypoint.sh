#!/bin/sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting migration..."
python manage.py migrate --noinput
echo "Migration finished."

echo "Starting Gunicorn..."
exec gunicorn -c gunicorn_conf.py -b :$PORT boutique_POS.wsgi
