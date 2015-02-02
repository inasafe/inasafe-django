SHELL := /bin/bash

default: web

run: build web

deploy: run
	@echo
	@echo "--------------------------"
	@echo "Brining up fresh instance "
	@echo "--------------------------"
	@fig run -p inasafe uwsgi python manage.py migrate
	#@run -p inasafe uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i inasafe_uwsgi_1 python manage.py collectstatic --noinput

rm:
	@echo
	@echo "--------------------------"
	@echo "Killing production instance!!! "
	@echo "--------------------------"
	@fig  -p inasafe kill
	@fig  -p inasafe rm

web:
	@echo
	@echo "--------------------------"
	@echo "Running in production mode"
	@echo "--------------------------"
	@fig  -p inasafe up -d web
	@dipall

sentry:
	@echo
	@echo "--------------------------"
	@echo "Running sentry production mode"
	@echo "--------------------------"
	@fig  -p inasafe up -d sentry
	@dipall


build:
	@echo
	@echo "--------------------------"
	@echo "Building in production mode"
	@echo "--------------------------"
	@fig  -p inasafe build

migrate:
	@echo
	@echo "--------------------------"
	@echo "Running migrate static in production mode"
	@echo "--------------------------"
	@fig -p inasafe run uwsgi python manage.py migrate

collectstatic:
	@echo
	@echo "--------------------------"
	@echo "Collecting static in production mode"
	@echo "--------------------------"
	#@fig -p inasafe run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i inasafe_uwsgi_1 python manage.py collectstatic --noinput

kill:
	@echo
	@echo "--------------------------"
	@echo "Killing in production mode"
	@echo "--------------------------"
	@fig -p inasafe kill

logs:
	@echo
	@echo "--------------------------"
	@echo "Showing uwsgi logs in production mode"
	@echo "--------------------------"
	@fig -p inasafe logs uwsgi

nginxlogs:
	@echo
	@echo "--------------------------"
	@echo "Showing nginx logs in production mode"
	@echo "--------------------------"
	@fig -p inasafe logs web

seed:
	@echo
	@echo "--------------------------"
	@echo "Seeding mapproxy in production mode"
	@echo "--------------------------"
	@fig -p inasafe run mapproxy /usr/local/bin/mapproxy-seed -f /mapproxy/mapproxy.yaml /mapproxy/seed.yaml

shell:
	@echo
	@echo "--------------------------"
	@echo "Shelling in in production mode"
	@echo "--------------------------"
	@fig -p inasafe run uwsgi /bin/bash

dbshell:
	@echo
	@echo "--------------------------"
	@echo "Shelling in in production database"
	@echo "--------------------------"
	@docker exec -t -i inasafe_db_1 psql -U docker -h localhost gis

qgis:
	@echo
	@echo "--------------------------"
	@echo "Running QGIS desktop in production mode"
	@echo "Make sure you have started the services with make run first"
	@echo "--------------------------"
	@xhost +; docker run --rm --name="qgis-desktop-2-4" \
	-i -t \
	--link inasafe_db_1:db \
	--link inasafe_qgisserver_1:qgisserver \
	--link inasafe_mapproxy_1:mapproxy \
	--volumes-from inasafe_qgisserver_1 \
	-v ${HOME}:/home/$(USER) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-e DISPLAY=unix$(DISPLAY) \
	kartoza/qgis-desktop:latest; xhost -
