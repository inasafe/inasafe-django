SHELL := /bin/bash

default: prod

prod: build uwsgi

uwsgi:
	@echo
	@echo "--------------------------"
	@echo "Running in production mode"
	@echo "--------------------------"
	@fig up -d --no-recreate uwsgi

build:
	@echo
	@echo "--------------------------"
	@echo "Building in production mode"
	@echo "--------------------------"
	@fig build

dev: devssh devmigrate devcollectstatic

devkill:
	@echo
	@echo "-----------------------------------"
	@echo "Killing developer environment"
	@echo "-----------------------------------"
	@fig -f fig-dev.yml kill
	@fig -f fig-dev.yml rm

devdb:
	@echo
	@echo "-----------------------------------"
	@echo "Running db in developer mode"
	@echo "-----------------------------------"
	@fig -f fig-dev.yml up -d --no-recreate devdb

devdblogs:
	@echo
	@echo "-----------------------------------"
	@echo "Running db logs in developer mode"
	@echo "press ctrl-c to exit log watcher"
	@echo "-----------------------------------"
	@fig -f fig-dev.yml logs devdb

devssh:
	@echo
	@echo "--------------------------"
	@echo "Running ssh server in developer mode"
	@echo "You can attach to this as a remote interpreter"
	@echo "in pycharm."
	@echo "--------------------------"
	@fig -f fig-dev.yml up -d --no-recreate dev

devmigrate:
	@echo
	@echo "--------------------------"
	@echo "Migrating in developer mode"
	@echo "--------------------------"
	@fig -f fig-dev.yml run devmigrate

devcollectstatic:
	@echo
	@echo "-----------------------------------"
	@echo "Collecting static in developer mode"
	@echo "-----------------------------------"
	@fig -f fig-dev.yml run devcollectstatic


devbuild: build
	@echo
	@echo "--------------------------"
	@echo "Building in developer mode"
	@echo "--------------------------"
	@fig build
	@fig -f fig-dev.yml build
