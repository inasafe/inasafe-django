#!/usr/bin/env bash

# Run database migrations
./manage.py migrate

# Run collectstatic
./manage.py collectstatic

# Run uwsgi
uwsgi --ini uwsgi.conf
