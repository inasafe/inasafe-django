SHELL := /bin/bash
PROJECT_ID := inasafedjango
DELAY = 10
LANG = en
TARGET_SERVER = realtime.inasafe.org

# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------

default: web

up: build web

complete-deploy: up wait migrate collectstatic makemessages compilemessages inasafe-worker indicator-worker reload status

wait:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Gives $(DELAY) second delay before running additional command "
	@echo "------------------------------------------------------------------"
	sleep $(DELAY)

deploy: up wait inasafe-worker indicator-worker
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh instance "
	@echo "You can access it on http://localhost:61100"
	@echo "------------------------------------------------------------------"

restart: kill deploy

ansible-check:
	@echo "Check ansible command"
	@ansible -i ansible/development/hosts all -m ping
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml --check --list-tasks --list-hosts $(ANSIBLE_ARGS)

setup-ansible:
	@echo "Setup configurations using ansible"
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml -v $(ANSIBLE_ARGS)

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building docker images"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) build

web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running web services"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d web

migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py migrate

makemigrations:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running make migrations "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py makemigrations

makemessages:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running make messages $(LANG) "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py makemessages -l $(LANG)

compilemessages:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running compile messages $(LANG) "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py compilemessages -l $(LANG)


collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static "
	@echo "------------------------------------------------------------------"
	# We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py collectstatic --noinput

inasafe-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d inasafe-worker

inasafe-worker-restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) restart inasafe-worker

inasafe-worker-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Stop celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) stop inasafe-worker

inasafe-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 inasafe-worker

indicator-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d indicator-worker

indicator-worker-restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) restart indicator-worker

indicator-worker-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) stop indicator-worker

indicator-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 indicator-worker

status:
	@docker-compose -p $(PROJECT_ID) ps

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) kill

rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing container instances!!! "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) rm

uwsgi-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50  uwsgi

db-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing db logs "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 db

nginx-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing nginx logs "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs web

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi /bin/bash

db-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in database containers"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec db /bin/bash

postgres-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in postgres"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec db psql -U docker -h localhost gis

qgis:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running QGIS desktop "
	@echo "Make sure you have started the services with make run first"
	@echo "------------------------------------------------------------------"
	@xhost +; docker run --rm --name="qgis-desktop-2.14" \
	-i -t \
	--link $(PROJECT_ID)_db_1:db \
	-v ${HOME}:/home/$(USER) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-e DISPLAY=unix$(DISPLAY) \
	kartoza/qgis-desktop:2.14.6; xhost -

dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from backups/latest.dmp "
	@echo "------------------------------------------------------------------"
	@echo "Copy .dmp file as latest.dmp in deployment/pg/dbbackup/backups/latest.dmp"
	@echo "Press any key to continue. Ctrl+C to cancel."
	@# - prefix causes command to continue even if it fails
	@read
	@echo "Dropping database gis"
	-@docker-compose -p $(PROJECT_ID) exec db su - postgres -c "dropdb gis"
	@echo "Create database gis"
	@docker-compose -p $(PROJECT_ID) exec db su - postgres -c "createdb -O docker -T template_postgis gis"
	@echo "Dumping to database gis"
	@docker-compose -p $(PROJECT_ID) exec dbbackup pg_restore /backups/latest.dmp | docker exec -i $(PROJECT_ID)_db_1 su - postgres -c "psql gis"

dbbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create `date +%d-%B-%Y`.dmp "
	@echo "Warning: backups/latest.dmp will be replaced with a symlink to "
	@echo "the new backup."
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	@docker-compose -p $(PROJECT_ID) exec dbbackup /backups.sh
	@docker-compose -p $(PROJECT_ID) exec dbbackup cat /var/log/cron.log | tail -2 | head -1 | awk '{print $4}'
	# backups is intentionally missing from front of first clause below otherwise symlink comes
	# out with wrong path...
	# trigger sftp backups
	@docker-compose -p $(PROJECT_ID) exec sftppgbackup /backups.sh
	@docker-compose -p $(PROJECT_ID) exec sftpmediabackup /backups.sh

pushbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Push local backup in sftpbackup to sftp remote server"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec sftppgbackup /start.sh push-to-remote-sftp
	@docker-compose -p $(PROJECT_ID) exec sftpmediabackup /start.sh push-to-remote-sftp

pullbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Pull remote sftp backup to local backup"
	@echo "------------------------------------------------------------------"
	@docker -p $(PROJECT_ID) exec sftppgbackup /start.sh pull-from-remote-sftp
	@docker -p $(PROJECT_ID) exec sftpmediabackup /start.sh pull-from-remote-sftp

mediasync:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Syncing media files from live server $(TARGET_SERVER)"
	@echo "------------------------------------------------------------------"
	rsync -av --progress --exclude *.mbtiles $(TARGET_SERVER):/home/data/inasafe-django/deployment/media/ media
	rsync -av --progress --exclude *.mbtiles $(TARGET_SERVER):/home/data/inasafe-django/django_project/core/settings/secret.py ../django_project/core/settings/

dbsync:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Syncing database files from live server $(TARGET_SERVER)"
	@echo "------------------------------------------------------------------"
	-@ssh $(TARGET_SERVER) "cd /home/data/inasafe-django/deployment; make dbbackup"
	rsync -av --progress $(TARGET_SERVER):/home/data/inasafe-django/deployment/sftp_backup/target/pg/latest.dmp backups
	rsync -av --progress $(TARGET_SERVER):/home/data/inasafe-django/deployment/sftp_backup/backups/pg backups

reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi uwsgi --reload /tmp/django.pid
