SHELL := /bin/bash
PROJECT_ID := inasafedjango

CONF_FILE := -f docker-compose.yml
CONF_HELP := Uses docker-compose.yml

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)
	CONF_HELP := Detecting Linux Environment. Use docker-compose-linux.yml
	CONF_FILE += -f docker-compose-linux.yml
endif
ifeq ($(UNAME_S),Darwin)
	CONF_HELP := Detecting OSX Environment. Use docker-compose-osx.yml
	CONF_FILE += -f docker-compose-osx.yml
endif

ifeq ($(MODE),dev)
	MODE_HELP := Using Development Environment. Use docker-compose-dev.yml
	CONF_FILE += -f docker-compose-dev.yml
	MODE_STRING := development
else
	MODE_HELP := Using Production Environment.
	MODE_STRING := production
endif

# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------

confinfo:
	@echo
	@echo $(CONF_HELP)
	@echo $(MODE_HELP)

default: web

run: build web

deploy: run migrate collectstatic
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh instance "
	@echo "You can access it on http://localhost:61100"
	@echo "------------------------------------------------------------------"

build: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) build

web: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) up -d web
	#@dipall

migrate: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) run uwsgi python manage.py migrate

collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	#@docker-compose $(CONF_FILE) -p $(PROJECT_ID) run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i $(PROJECT_ID)_uwsgi_1 python manage.py collectstatic --noinput

djcelery-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running celery worker in dev mode"
	@echo "------------------------------------------------------------------"
	@docker exec -it $(PROJECT_ID)_uwsgi_1 python manage.py --settings=core.settings.dev_docker_celeryworker celery worker --loglevel=info

kill: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) kill

rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing $(MODE_STRING) instance!!! "
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) rm

logs: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) logs uwsgi

nginxlogs: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing nginx logs in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(CONF_FILE) -p $(PROJECT_ID) logs web

shell: confinfo
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	#@docker-compose $(CONF_FILE) -p $(PROJECT_ID) run uwsgi /bin/bash
	@docker exec -it $(PROJECT_ID)_uwsgi_1 /bin/bash

dbshell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in $(MODE_STRING) database"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_db_1 psql -U docker -h localhost gis

qgis:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running QGIS desktop in $(MODE_STRING) mode"
	@echo "Make sure you have started the services with make run first"
	@echo "------------------------------------------------------------------"
	@xhost +; docker run --rm --name="qgis-desktop-2-4" \
	-i -t \
	--link $(PROJECT_ID)_db_1:db \
	--link $(PROJECT_ID)_qgisserver_1:qgisserver \
	--link $(PROJECT_ID)_mapproxy_1:mapproxy \
	--volumes-from $(PROJECT_ID)_qgisserver_1 \
	-v ${HOME}:/home/$(USER) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-e DISPLAY=unix$(DISPLAY) \
	kartoza/qgis-desktop:latest; xhost -

dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from backups/latest.dmp in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	-@docker exec -t -i $(PROJECT_ID)_db_1 su - postgres -c "dropdb gis"
	@docker exec -t -i $(PROJECT_ID)_db_1 su - postgres -c "createdb -O docker -T template_postgis gis"
	@docker exec -t -i $(PROJECT_ID)_dbbackup_1 pg_restore /backups/latest.dmp | docker exec -i $(PROJECT_ID)_db_1 su - postgres -c "psql gis"

dbbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create `date +%d-%B-%Y`.dmp in $(MODE_STRING) mode"
	@echo "Warning: backups/latest.dmp will be replaced with a symlink to "
	@echo "the new backup."
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	docker exec -t -i $(PROJECT_ID)_dbbackup_1 /backups.sh
	@docker exec -t -i $(PROJECT_ID)_dbbackup_1 cat /var/log/cron.log | tail -2 | head -1 | awk '{print $4}'
	# backups is intentionally missing from front of first clause below otherwise symlink comes
	# out with wrong path...
	# trigger sftp backups
	@docker exec -t -i $(PROJECT_ID)_sftppgbackup_1 /backups.sh
	@docker exec -t -i $(PROJECT_ID)_sftpmediabackup_1 /backups.sh

pushbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Push local backup in sftpbackup to sftp remote server"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_sftppgbackup_1 /start.sh push-to-remote-sftp
	@docker exec -t -i $(PROJECT_ID)_sftpmediabackup_1 /start.sh push-to-remote-sftp

pullbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Pull remote sftp backup to local backup"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_sftppgbackup_1 /start.sh pull-from-remote-sftp
	@docker exec -t -i $(PROJECT_ID)_sftpmediabackup_1 /start.sh pull-from-remote-sftp

reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project in $(MODE_STRING) mode"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_uwsgi_1 uwsgi --reload  /tmp/django.pid

create-machine:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Creating a docker machine. Only useful for OSX and Windows"
	@echo "------------------------------------------------------------------"
	@docker-machine create --driver virtualbox inasafe-django
	@echo "Now attach to your machine by doing:"
	@echo '"$(docker-machine env inasafe-django)"'

