# Managing your docker deployed site

This document explains how to do various sysadmin related tasks when your 
site has been deployed under docker.

## Build your docker images and run them

You can simply run the provided script and it will build and deploy the docker
images for you in **production mode**.

``
fig build
fig up -d uwsgi
fig run collectstatic
fig run migrate
``

To create a staging site (or run any of the provided management scripts in 
staging mode), its the same procedure except you need to use the 
``fig-staging.yml`` environment variable e.g.::

``
fig -f fig-staging.yml build
fig -f fig-staging.yml up -d staginguwsgi
fig -f fig-staging.yml run stagingcollectstatic
fig -f fig-staging.yml run stagingmigrate
``

## Setup nginx reverse proxy

You should create a new nginx virtual host - please see 
``*-nginx.conf`` in the root directory of the source for an example. There is 
one provided for production and one for staging.

Simply add the example file to your ``/etc/nginx/sites-enabled/`` directory 
and then modify the contents to match your local filesystem paths. Then use

```
sudo nginx -t
```

To verify that your configuration is correct and then reload / restart nginx
e.g.

```
sudo /etc/init.d/nginx restart
```

## Management scripts

The following scripts are supplied:

### Create docker env

**Usage example:** ``fig build``

**Arguments:** [-f fig-dev.yml|fig-staging.yml]
 
**Description:** Running this script will create the docker images needed to
deploy your application. The -f argument is optional (if omitted, commands will
be run in production mode).

### Run in production mode

**Usage example:** ``fig up -d uwsgi``

**Arguments:** 

* ``-d`` - specifies that containers should be run in the background as daemons.

**Description:** Running this script will deploy your application in 
**production** mode. Note that we recommend running production mode in a 
separate checkout from your staging mode.

After creating the images (or fetching them if they are being used from 
the docker hub repository), container instances will be deployed and you should
then do any initialisation that needs to be carried out (
e.g. migrations, collect static) see below for details.

Once the command is run, you should see a number of docker containers running
and linking to each other when you run the ``docker ps`` command. You 
should also be able to visit the site in your web browser after ensuring that
your nginx proxy configuration is correct (see above).

### Run in staging mode

**Usage example:** ``fig -f fig-staging.yml up -d staginguwsgi``

**Arguments:** 
* ``-f`` - specifies that the fig staging config should be used.
* ``-d`` - specifies that containers should be run in the background as daemons.

**Description:** Running this script will deploy your application in staging 
mode. Note that we recommend running staging mode in a separate checkout.

After creating the images (or fetching them if they are being used from 
the docker hub repository), container instances will be deployed and you should
then do any initialisation that needs to be carried out (
e.g. migrations, collect static) see below for details.

Once the command is run, you should see a number of docker containers running
and linking to each other when you run the ``docker ps`` command. You 
should also be able to visit the site in your web browser after ensuring that
your nginx proxy configuration is correct (see above).


### Collect static

**Usage:** ``fig [-f fig-staging.yml|fig-dev.yml]<collectstatic|stagingcollectstatic|devcollectstatic>``

**Example Usage:** 

* ``fig collectstatic``
* ``fig -f fig-staging.yml stagingcollectstatic``

**Arguments:** 
* ``-f`` - specifies that the fig staging config should be used.
* ``-d`` - specifies that containers should be run in the background as daemons.
 
 
**Description:** Running this script will create a short lived docker container
based on your production django image. It will mount your code tree under 
``/home/web`` via a docker shared volume and create a link to your database
container, using docker's ``--link`` directive. It will then run 

```django manage.py collectstatic --noinput --settings=core.settings.prod_docker```

or 

```django manage.py collectstatic --noinput --settings=core.settings.staging_docker```

or

```django manage.py collectstatic --noinput --settings=core.settings.dev_docker```

Depending on whether you supply the staging, dev or production fig yml file.

### Run migrations


**Usage:** ``fig [-f fig-staging.yml|fig-dev.yml]<migrate|stagingmigrate|devmigrate>``

**Example Usage:** 

* ``fig migrate``
* ``fig -f fig-staging.yml stagingcollectstatic``

**Arguments:** 
* ``-f`` - specifies that the fig staging config should be used.
* ``-d`` - specifies that containers should be run in the background as daemons.
 
 
**Description:** Running this script will create a short lived docker container
based on your production django image. It will mount your code tree under 
``/home/web`` via a docker shared volume and create a link to your database
container, using docker's ``--link`` directive. It will then run 

```django manage.py migrate --noinput --settings=core.settings.prod_docker```

or 

```django manage.py migrate --noinput --settings=core.settings.staging_docker```

or

```django manage.py migrate --noinput --settings=core.settings.dev_docker```

Depending on whether you supply the staging, dev or production fig yml file.


### Bash prompt

**Usage:** ``fig [-f fig-staging.yml|fig-dev.yml.yml]<shell|stagingshell|devshell>``

**Example Usage:** 

* ``fig shell``
* ``fig -f fig-staging.yml stagingshell``

**Arguments:** 
* ``-f`` - specifies that the fig staging config should be used.
* ``-d`` - specifies that containers should be run in the background as daemons.
 
 
**Description:** Running this script will create a short lived docker container
based on your production django image. It will mount your code tree under 
``/home/web`` via a docker shared volume and create a link to your database
container, using docker's ``--link`` directive. It will then drop you into a
bash prompt (note that you may need to press ``enter`` after running the 
command in order to activate the shell). The bash environment that you land up
in will depend on whether you supply the staging, dev or production fig 
``yml`` file.


### Managing containers

Please refer to the general [fig documentation](http://www.fig.sh/cli.hyml)
for further notes on how to manage the infrastructure using fig.

# Configuration options

You can configure the base port used and various other options like the
image organisation namespace and postgis user/pass by editing the ``fig*.yml``
files.
