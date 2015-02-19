SHELL := /bin/bash

# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------

default: web

run: build web

deploy: run migrate collectstatic
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh instance "
	@echo "You can access it on http://localhost:61100"
	@echo "------------------------------------------------------------------"

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe build

web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe up -d web
	@dipall

migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe run uwsgi python manage.py migrate

collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in production mode"
	@echo "------------------------------------------------------------------"
	#@fig -p inasafe run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i inasafe_uwsgi_1 python manage.py collectstatic --noinput

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in production mode"
	@echo "------------------------------------------------------------------"

	@fig -p inasafe kill

rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing production instance!!! "
	@echo "------------------------------------------------------------------"
	@fig -p inasafe rm

logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe logs uwsgi

nginxlogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing nginx logs in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe logs web

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in production mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe run uwsgi /bin/bash

dbshell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in production database"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i inasafe_db_1 psql -U docker -h localhost gis

qgis:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running QGIS desktop in production mode"
	@echo "Make sure you have started the services with make run first"
	@echo "------------------------------------------------------------------"
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



# ----------------------------------------------------------------------------
#    S T A G I N G     C O M M A N D S
# ----------------------------------------------------------------------------

staging-run: staging-build staging-web

staging-deploy: staging-run staging-migrate staging-collectstatic
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh staging instance "
	@echo "You can access it on http://localhost:61101"
	@echo "------------------------------------------------------------------"

staging-build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging build

staging-web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging up -d stagingweb
	@dipall

staging-migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging run uwsgi python manage.py migrate

staging-collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in staging mode"
	@echo "------------------------------------------------------------------"
	#@fig -p inasafe-staging run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i inasafestaging_uwsgi_1 python manage.py collectstatic --noinput

staging-kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in staging mode"
	@echo "------------------------------------------------------------------"

	@fig -p inasafe-staging kill

staging-rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing staging instance!!! "
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging rm

staging-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging logs uwsgi

staging-nginxlogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing nginx logs in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging logs web

staging-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in staging mode"
	@echo "------------------------------------------------------------------"
	@fig -p inasafe-staging run uwsgi /bin/bash

staging-dbshell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in staging database"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i inasafestaging_db_1 psql -U docker -h localhost gis

staging-qgis:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running QGIS desktop in staging mode"
	@echo "Make sure you have started the services with make run first"
	@echo "------------------------------------------------------------------"
	@xhost +; docker run --rm --name="qgis-desktop-2-4" \
	-i -t \
	--link inasafestaging_db_1:db \
	--link inasafestaging_qgisserver_1:qgisserver \
	--volumes-from inasafe_qgisserver_1 \
	-v ${HOME}:/home/$(USER) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-e DISPLAY=unix$(DISPLAY) \
	kartoza/qgis-desktop:latest; xhost -
