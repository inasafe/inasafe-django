# Test
# Welcome to the InaSAFE Web code base!

[InaSAFE](http://insafe.org) is a contingency planning and preparedness tool
for disasters. This django project provides various resources related to the
InaSAFE project in particular:

* A user map
* Realtime Earthquake Reports
* Realtime Flood Reports
* Realtime Ash Reports

You can visit a running instance of this project at
[realtime.inasafe.org](http://realtime.inasafe.org).

# Status

These badges reflect the current status of our development branch:

Tests status: [![Build Status](https://travis-ci.org/inasafe/inasafe-django.svg)](https://travis-ci.org/inasafe/inasafe-django)

Coverage status: [![Coverage Status](https://coveralls.io/repos/inasafe/inasafe-django/badge.png?branch=develop)](https://coveralls.io/r/inasafe/inasafe-django?branch=develop)

Development status: [![Stories in Ready](https://badge.waffle.io/AIFDR/inasafe-django.svg?label=ready&title=Ready)](http://waffle.io/inasafe/inasafe-django) [![Stories in Ready](https://badge.waffle.io/AIFDR/inasafe-django.svg?label=In%20Progress&title=In%20Progress)](http://waffle.io/inasafe/inasafe-django)

# License

Data: [Open Database License](http://opendatacommons.org/licenses/odbl/)
Code: [Free BSD License](http://www.freebsd.org/copyright/freebsd-license.html)

Out intention is to foster wide spread usage of the data and the code that we
provide. Please use this code and data in the interests of humanity and not for
nefarious purposes.

# Setup instructions

## Production

We provide for simple deployment under a mix of docker and ansible. Please 
see the [Docker Readme](deployment/README-docker.md)  file for details.

## For local development

We provide for simple deployment under a mix of docker and ansible. Please 
see the [Docker Readme](deployment/README-docker.md) file for details.

The following method was not needed if you use our docker orchestration 
because it will set up everything. Instructions below was left for knowledge 
purposes.

### Install dependencies

```
virtualenv venv
source venv/bin/activate
pip install -r REQUIREMENTS-dev.txt
```

### Create your dev profile

```
cd django_project/core/settings
cp dev_timlinux.py dev_${USER}.py
```

Now edit dev_<your username> setting your database connection details as
needed. We assume you have created a postgres (with postgis extentions)
database somewhere that you can use for your development work. See
[http://postgis.net/install/](http://postgis.net/install/) for details on doing
that.

### Running migrate, collect static, and development server

Prepare your database and static resources by doing this:

```
virtualenv venv
source venv/bin/activate
cd django_project
python manage.py migrate --settings=core.settings.dev_${USER}
python manage.py collectstatic --noinput --settings=core.settings.dev_${USER}
python manage.py runserver --settings=core.settings.dev_${USER}
```

### Running production and development configuration using docker

We are heading towards using docker environment for production and development
purposes between machines. By using Pycharm, we are able to setup development 
environment for debugging purposes

#### Prerequisites

We are using multi docker-compose configuration files. This feature is only
available for docker-compose version 1.5.0rc2 above. With this feature, Makefile 
configuration will adapt accordingly for Linux, OSX, and Windows environment. 
This resolves some issues with postgis containers not able to be created in OSX 
and Windows.

#### Configuration

To run make, go to ```deployment``` folder.

```
cd deployment
make build # will build environment and docker images for production purposes
make run # will run the server for production purposes
make collectstatic # will process static files (compressing, minifying)
make migrate # will migrate the database
make deploy # will do build, run, migrate, and collectstatic in one command
```

To run the make command for development environment, just append ```MODE=dev``` 
in make command.

```
make deploy MODE=dev # deploy in development environment
```

#### Using development environment

A development environment has several benefit for code debugging:

* Ability to connect to python interpreter inside docker
* Ability to connect to postgis db inside docker
* Ability to run django deploy inside docker
* Ability to debug django deploy inside docker (so the code will be able to 
  get a hotload feature)

All of the above will be explained in different section


## Using Local Docker Development Environment Configuration

Before configuration, make sure you run the environment using dev Mode:

```
make run MODE=dev
```

### Connect Pycharm remote interpreter to docker

1. Go to Pycharm settings > Project Interpreter > Add remote interpreter.

2. Choose SSH and fill the following field:

```
Host: (your docker machine IP, or just localhost in linux docker environment)
Port: 61103
Username: root
Auth type: password
Password: docker
Interpreter path: /usr/local/bin/python
```

3. Press Ok

### Connect postgis db using PgAdmin 3

Your docker postgis db can be accessed using your docker machine IP (or just 
localhost in linux), with port 6543, user ```docker``` and password ```docker```.
Just adapt pgAdmin 3 connection using this information.


### Run Django using Pycharm
 
After creating remote docker interpreter for this project, you can use the 
interpreter to create django configuration.

1. Go to Run > Edit Configurations
2. Fill the following information

```
Host: 0.0.0.0 # so we can access it outside docker machine
Port: 8080 # we already portforward port 8080 to the outside of docker machine
Python Interpreter: (Choose remote docker interpreter that we made)
Environment: Add environment for DJANGO_SETTINGS_MODULE=core.settings.dev_docker
	If you want production settings (compressed staticfiles), use core.settings.prod_docker
```

3. Edit file path mappings. Go to Tools > Deployment > Configurations

4. Add new SFTP Connections. Fill the Following information

```
Visible for this project only: Check this
Type: SFTP
Host: Your docker machine IP (or localhost for linux)
Port: 61103
Root path: /
User: root
Auth type: password
Password: docker
```
   
   Additionally you can check that the configurations is correct by clicking
   Test SFTP connections.
   
5. Add Path mappings by clicking Mappings tab. Fill out the following mappings

 ```
(Your django_project directory) to /home/web/django_project
(Your deployment/static directory) to /home/web/static

Optionally, you can also add this:
(Your deployment/media directory) to /home/web/media
(Your deployment/reports directory) to /home/web/reports
```
   
6. To run django, click Run or Debug respectively
   In debug mode, you can put breakpoints like you would do in local dev environment.
