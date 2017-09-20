#!/usr/bin/env bash

# Run database migrations
echo "Run database migrations"
./manage.py migrate

# Run collectstatic
echo "Run collectstatic"
./manage.py collectstatic --noinput

# Run compile messages

./manage.py compilemessages -l id

# Run uwsgi
uwsgi --ini /uwsgi.conf
