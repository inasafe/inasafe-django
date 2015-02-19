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

## Production, Staging

We provide for simple deployment under docker. Please see the 
deployment/README-docker.md file for details.

## For local development

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
