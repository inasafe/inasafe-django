# Welcome to the InaSAFE Web code base!

[InaSAFE](http://insafe.org) is a contingency planning and preparedness tool 
for disasters. This django project provides various resources related to the
InaSAFE project in particular:

* A user map

**Please note that this project is in the early phase of its development.**

You can visit a running instance of this project at 
[users.inasafe.org](http://inasafe.org).

# Status

These badges reflect the current status of our development branch:

Tests status: [![Build Status](https://travis-ci.org/AIFDR/inasafe-django.svg)](https://travis-ci.org/AIFDR/inasafe-django)

Coverage status: [![Coverage Status](https://coveralls.io/repos/inasafe/inasafe-django/badge.png?branch=develop)](https://coveralls.io/r/inasafe/inasafe-django?branch=develop)

Development status: [![Stories in Ready](https://badge.waffle.io/inasafe/inasafe-django.svg?label=ready&title=Ready)](http://waffle.io/inasafe/inasafe-django) [![Stories in Ready](https://badge.waffle.io/inasafe/inasafe-django.svg?label=In%20Progress&title=In%20Progress)](http://waffle.io/inasafe/inasafe-django)

# License

Data: [Open Database License](http://opendatacommons.org/licenses/odbl/)
Code: [Free BSD License](http://www.freebsd.org/copyright/freebsd-license.html)

Out intention is to foster wide spread usage of the data and the code that we provide. Please use this code and data in the interests of humanity and not for nefarious purposes.

# Setup instructions

## Simple deployment under docker

### Overview

You need two docker containers:

* A postgis container
* A uwsgi container

We assume you are running nginx on the host and we will set up a reverse
proxy to pass django requests into the uwsgi container. Static files will
be served directly using nginx on the host.

A convenience script is provided under ``scripts\create_docker_env.sh`` which
should get everything set up for you. Note you need at least docker 1.2 - use
the [installation notes](http://docs.docker.com/installation/ubuntulinux/) 
on the official docker page to get it set up.

### Check out the source


First checkout out the source tree:

```
mkdir -p ~/production-sites
mkdir /tmp/inasafe-tmp
cd ~/production-sites
git clone git://github.com/inasafe/inasafe-django.git
```

### Build your docker images and run them

You can simply run the provided script and it will build and deploy the docker
images for you.

``
cd inasafe
scripts\create_docker_env.sh
``

### Setup nginx reverse proxy

You should create a new nginx virtual host - please see 
``inasafe-nginx.conf`` in the root directory of the source for an example.


## For local development

### Install dependencies

```
virtualenv venv
source venv/bin/activate
pip install -r REQUIREMENTS-dev.txt
nodeenv -p --node=0.10.31
npm -g install yuglify
```

### Create your dev profile


```
cd django_project/core/settings
cp dev_dodobas.py dev_${USER}.py
```

Now edit dev_<your username> setting your database connection details as
needed. We assume you have created a postgres (with postgis extentions) 
database somewhere that you can use for your development work. See 
[http://postgis.net/install/](http://postgis.net/install/) for details on doing
that.

### Running collect and migrate static

Prepare your database and static resources by doing this:

```
virtualenv venv
source venv/bin/activate
cd django_project
python manage.py migrate
python manage.py collectstatic --noinput --settings=core.settings.dev_${USER}
```

**Note:** You can also develop in docker using the instructions provided in
[README-dev.md](https://github.com/aifdr/inasafe-django/blob/develop/README-dev.md).




