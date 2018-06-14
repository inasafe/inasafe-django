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

down:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shutdown docker containers"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) down

complete-deploy: up wait migrate collectstatic makemessages compilemessages inasafe-worker indicator-worker realtime-worker headless-worker reload status

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

restart: down deploy

ansible-check:
	@echo "Check ansible command"
	@ansible -i ansible/development/hosts all -m ping
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml --check --list-tasks --list-hosts $(ANSIBLE_ARGS)

setup-ansible:
	@echo "Setup configurations using ansible"
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml -v $(ANSIBLE_ARGS)

check-flake8:
	@echo "Check flake 8"
	@flake8 ../django_project

pull-external-services:
	@echo "Pull InaSAFE Realtime"
	@docker-compose -p $(PROJECT_ID) pull realtime-worker
	@echo "Pull InaSAFE Headless"
	@docker-compose -p $(PROJECT_ID) pull headless-worker

pull-external-services-docker:
	@echo "Pull InaSAFE Realtime"
	@docker pull inasafe/realtime_hazard-processor
	@echo "Pull InaSAFE Headless"
	@docker pull inasafe/headless_processor

coverage-tests:
	@docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test realtime --noinput --liveserver=0.0.0.0:8080 -v 2

integration-tests-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running integration tests celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d integration-test-worker

integration-tests-worker-restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart integration tests celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) restart integration-test-worker

integration-tests-worker-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Stop integration tests celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) stop integration-test-worker

integration-tests-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running integration tests celery worker logs"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 integration-test-worker

combined-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing combined worker logs"
	@echo "------------------------------------------------------------------"
	@{ make realtime-worker-logs & make headless-worker-logs & make inasafe-worker-logs; }

combined-integration-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing combined integration worker logs"
	@echo "------------------------------------------------------------------"
	@{ make realtime-worker-logs & make headless-worker-logs & make integration-tests-worker-logs & make integration-tests-runner-logs; }

integration-tests: realtime-worker headless-worker integration-tests-worker
	@docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestEarthquakeTasks
	@make integration-tests-worker-restart
	@docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestFloodTasks
	@make integration-tests-worker-restart
	@docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestAshTasks

integration-tests-with-logs: realtime-worker headless-worker integration-tests-worker
	@-{ make headless-worker-logs & make realtime-worker-logs & make integration-tests-worker-logs & docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestEarthquakeTasks; }
	@-make integration-tests-worker-restart
	@-{ make headless-worker-logs & make realtime-worker-logs & make integration-tests-worker-logs & docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestFloodTasks; }
	@-make integration-tests-worker-restart
	@-{ make headless-worker-logs & make realtime-worker-logs & make integration-tests-worker-logs & docker-compose -p $(PROJECT_ID) exec uwsgi coverage run -p --branch --source='.' manage.py test --liveserver=0.0.0.0:8080 --noinput realtime.tests.test_scenarios.TestAshTasks; }

retrieve-context-data:
	@docker run --rm -d --name analysis_context inasafe/analysis_context_image:v4.4.0 tail -f /dev/null
	@docker cp -a analysis_context:/data/. headless-data/contexts
	@docker stop analysis_context

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

transifex-pull:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Download translation from Transifex ${LANG}"
	@echo "------------------------------------------------------------------"
	@cd ../; tx pull -l ${LANG}

transifex-push-language:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Push translation to Transifex for language $(LANG)"
	@echo "------------------------------------------------------------------"
	@cd ../; tx push -t -l $(LANG)

transifex-push-source:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Push translation source to Transifex"
	@echo "------------------------------------------------------------------"
	@cd ../; tx push -s

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
	@echo "Running celery worker logs"
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
	@echo "Running celery worker logs"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 indicator-worker

realtime-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running InaSAFE Realtime celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d realtime-worker

realtime-worker-shell:
	@docker-compose -p $(PROJECT_ID) exec realtime-worker /bin/bash

realtime-worker-restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart InaSAFE Realtime celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) restart realtime-worker

realtime-worker-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Stop InaSAFE Realtime celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) stop realtime-worker

realtime-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running InaSAFE Realtime celery worker logs"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 realtime-worker

realtime-shakemap-monitor-logs:
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 shakemap-monitor

realtime-shakemap-corrected-monitor-logs:
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 shakemap-corrected-monitor

headless-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running InaSAFE Headless celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d headless-worker

headless-worker-shell:
	@docker-compose -p $(PROJECT_ID) exec headless-worker /bin/bash

headless-worker-restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restart InaSAFE Headless celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) restart headless-worker

headless-worker-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Stop InaSAFE Headless celery worker "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) stop headless-worker

headless-worker-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running InaSAFE Headless celery worker logs"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs -f --tail=50 headless-worker

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
	@docker-compose -p $(PROJECT_ID) exec db "pg_restore /backups/latest.dmp | su - postgres -c 'psql gis'"

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
	rsync -av --progress $(TARGET_SERVER):/home/data/inasafe-django/deployment/sftp_backup/target/pg/latest.dmp pg/dbbackup/backups
	rsync -av --progress $(TARGET_SERVER):/home/data/inasafe-django/deployment/sftp_backup/backups/pg pg/dbbackup/backups

reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi uwsgi --reload /tmp/django.pid

contexts-sync:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running contexts btsync"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d contexts-btsync

qgis-templates-sync:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running QGIS templates btsync"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d qgis-templates-btsync

import-kelurahan-boundary:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Import kelurahan boundary"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py \
	importfloodboundary /home/headless/contexts/flood/exposure/DKI_Jakarta_Population_Dukcapil_2013_WGS84.shp '' NAMA_KELUR 7 Kelurahan

load-flood-test-data:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Load flood test data"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) exec uwsgi python manage.py loadfloodtestdata
