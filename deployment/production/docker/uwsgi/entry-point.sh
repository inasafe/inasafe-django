#!/usr/bin/env bash

# Run database migrations
echo "Run database migrations"
./manage.py migrate

# Run collectstatic
echo "Run collectstatic"
./manage.py collectstatic --noinput

# Run compile messages

echo "Compile messages"
./manage.py compilemessages -l id

if [ "$DEBUG" == "True" ]; then
	echo "Running in debug mode"
    python manage.py runserver 0.0.0.0:8000
else
	# Run uwsgi
	echo "Running in prod mode"
	uwsgi --ini /uwsgi.conf
fi
