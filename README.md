# Welcome to the InaSAFE Web code base!

[InaSAFE](http://insafe.org) is a contingency planning and preparedness tool
for disasters. This django project provides various resources related to the
InaSAFE project in particular:

* A user map
* more to come

**Please note that this project is in the early phase of its development.**

You can visit a running instance of this project at
[users.inasafe.org](http://inasafe.org).

# Status

These badges reflect the current status of our development branch:

Tests status: [![Build Status](https://travis-ci.org/AIFDR/inasafe-django.svg)](https://travis-ci.org/AIFDR/inasafe-django)

Coverage status: [![Coverage Status](https://coveralls.io/repos/AIFDR/inasafe-django/badge.png?branch=develop)](https://coveralls.io/r/AIFDR/inasafe-django?branch=develop)

Development status: [![Stories in Ready](https://badge.waffle.io/AIFDR/inasafe-django.svg?label=ready&title=Ready)](http://waffle.io/AIFDR/inasafe-django) [![Stories in Ready](https://badge.waffle.io/AIFDR/inasafe-django.svg?label=In%20Progress&title=In%20Progress)](http://waffle.io/AIFDR/inasafe-django)

# License

Data: [Open Database License](http://opendatacommons.org/licenses/odbl/)
Code: [Free BSD License](http://www.freebsd.org/copyright/freebsd-license.html)

Out intention is to foster wide spread usage of the data and the code that we
provide. Please use this code and data in the interests of humanity and not for
nefarious purposes.

# Setup instructions

## Simple deployment under docker

### Overview

You need two docker containers:

* A postgis container
* A uwsgi container

We assume you are running nginx on the host and we will set up a reverse
proxy to pass django requests into the uwsgi container. Static files will
be served directly using nginx on the host.


### Check out the source


First checkout out the source tree:

```
git clone git://github.com/aifdr/inasafe-django.git
```

### Build your docker images and run them

You need to have http://docker.io and http://www.fig.sh/ installed first.

Note you need at least docker 1.2 - use
the [installation notes](http://docs.docker.com/installation/ubuntulinux/)
on the official docker page to get it set up.

Fig will build and deploy the docker images for you. Note if you are using
``apt-cacher-ng`` (we recommend it as it will dramatically speed up build
times), be sure to edit ``docker-prod/71-apt-cacher-ng`` and comment out
existing lines, adding your own server. Alternatively if you wish to fetch
packages are downloaded directly from the internet, ensure that all lines are
commented out in your hosts:

* ``docker-prod/71-apt-cacher-ng``
* ``docker-dev/71-apt-cacher-ng``


```
fig build
fig up -d web
fig run web python manage.py migrate
fig run web python manage.py collectstatic --noinput
```

Or if you are on a system that supports Make you can use the convenience script:

```
make deploy
```

### Setup nginx reverse proxy

You should create a new nginx virtual host - please see
``inasafe_django_nginx.conf`` in the root directory of the source for an
example.

Take care also that nginx on your host has recursive read, execute permissions
down to the static folder in <project base>/django_project/static. For example:

```
chmod a+X /home/timlinux/dev/python/inasafe-django/django_project/static
```


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

**Note:** You can also develop in docker using the instructions provided in
[README-dev.md](https://github.com/aifdr/inasafe-django/blob/develop/README-dev.md).




