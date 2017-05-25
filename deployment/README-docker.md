# Deploying and configuring with ansible and docker

This documentation is intended to explain on how to configure the project and 
deploy it locally for development or deploying it on the server for production 
or staging purposes. These setup is aimed to quickly configure the project 
using ansible (copy and configure necessary files).

## Ansible configuration

Of course, make sure you have ansible in your machine. Next step, configure 
various facts and variables in [ansible vars file](ansible/development/group_vars/all.sample.yml), 
then create a new file called `all` or `all.yml` with modified configuration.
For a full detail and comments for various variables related, see: [all.sample.yml](ansible/development/group_vars/all.sample.yml),

**What Ansible will do**

Ansible will setup and configure all necessary files for running InaSAFE Django 
web app based on your configuration. This helps to put all the settings in 
one file. If you changed server IP or other variables you can change it in 
`all.yml` file and run setup again. Ansible will generate the settings but will
not run your django app.

## Docker orchestration

The orchestration we use is a combination of Makefile and docker-compose. We 
are using docker-compose to generate necessary docker containers and use 
Makefile to simplify some commands.

### First build

If this is your first build, you have to chain several command to build docker 
images, running database migration and generating staticfiles. Execute these 
command in stages:

```
make build
```

This will build all necessary docker images based on your configuration (production) 
or development.

```
make up
```

This will instantiate containers and run it. There are some containers that uses 
prebuilt docker images, so you probably need to download some images.

```
make migrate
```

This will execute database migration and populate your db container with 
necessary postgis tables. You should run this if you change your models.

```
make collectstatic
```

This will generate compiled/minified staticfiles such as javascript and/or css 

```
make inasafe-worker 
```

This will run InaSAFE related celery worker.

```
make indicator-worker
```

This will run indicator worker, a service to make sure InaSAFE Django and 
InaSAFE Realtime processor is connected.

```
make compilemessages
```

This will compile django i18n related messages. Used for translation.

Those commands above are individual make commands that needs to be executed 
depending on the situation. For example, if you just want to have the 
necessary containers running in development mode, you can run:

```
make up
```

(assuming you already use build, migrate, and collectstatic before.)

Then, the last, to kill all the containers, run:

```
make kill
```

If you want to delete and rebuilt containers, you could also run:

```
make rm
```

### Complete Deploy

Sometimes, if you run in a production server, you just want to execute 
one command to do everything. You can chain your command (because it is 
just a make command), like this:

```
make up inasafe-worker indicator-worker
```

Sometimes, the database failed to load, because it is accessed before it was 
ready. In this case, you could use wait command

```
make up wait inasafe-worker indicator-worker
```

The default wait time for that command is 10 seconds. However, if you think 
that this is too long or too short, you can change it by passing DELAY argument 

```
make up wait DELAY=5 inasafe-worker indicator-worker
```

To make it more simple, we provide a shortcut command for it.

```
make complete-deploy
```

Above command will execute all command from build until status. 
You can look at the Makefile to see the chains.

There is also a more short command, omitting migrate and collectstatic 
since we don't do that too often.

```
make deploy
```

Or if you just wanted to restart the whole services, which is actually 
killing the service and then do deploy.

```
make restart
```

Sometimes, you update some code or doing migration/collectstatic on production 
server. In this case, Django won't immediately reload, because Django is loaded 
using uwsgi. To make the web reload, execute this command. This will reload 
nginx, without killing the whole container stack.

```
make reload
```

### Celery workers

InaSAFE Django uses two celery workers. The first one is to handle all 
InaSAFE Realtime requests, the second one is to perform scheduled tasks.

Execute this command to start InaSAFE Realtime worker

```
make inasafe-worker
```

Execute this command to start InaSAFE Indicator worker, performing scheduled 
tasks and indicator tasks to make sure it is connected with InaSAFE Realtime 
processor.

```
make indicator-worker
```

Sometimes celery worker hangs, but doesn't get killed. In this case, we might 
need to restart the worker. Just append `-restart` to the command.

```
make inasafe-worker-restart # or
make indicator-worker-restart
```

### Logging

We provided a command to attach to container logging.

To view/attach to uwsgi-logs

```
make uwsgi-logs
```

To view/attach to nginx-logs

```
make nginx-logs
```

To view/attach to database logs

```
make db-logs
```

To view/attach to celery worker logs

```
make inasafe-worker-logs
make indicator-worker-logs
```

These logs is helpful for debugging purposes in production mode.

### Get into shell

There are times when you need to go inside the container. If you already familiar 
with docker-compose, you can do it easily. We also made shortcut command 
for this task.

This will take you to uwsgi container, where you can interact with django manage 
command.

```
make shell
```

This will take you to database container, where you can inspect backup manually 
or log into psql

```
make db-shell
```

This will take you directly to psql

```
make postgres-shell
```

### Managing backups

We created a shortcut command to generate snapshots of postgres and media. 

```
make dbbackup
```

You can chain this command to a cron job so a backup will be generated in 
regular interval. For example to generate backup daily at midnight:

```
crontab -e
# This will open cron table
# Write your schedule in the table:
0 0 * * * cd [inasafe-django directory]/deployment && make dbbackup
```

It is often that we need to create several backup snapshots based on the day. 
For this task, we are using our custom built containers, sftppgbackup for 
backing up postgres database, and sftpmediabackup for backing up media folder. 
These containers works by archiving a target folder. So it doesn't generate 
postgis dump. We need to chain this service with dbbackup container.

To explain how the chain works, sftppgbackup will run a nightly backup at 11 PM. 
That means, if you want, the database should already be backed up before 11 PM. 
That way, sftppgbackup will archive the latest backup for that day. In order to 
do that, specify your cron job to be executed before 11 PM. The following is 
an example to execute dbbackup every 10 PM.

```
crontab -e
# This will open cron table
# Write your schedule in the table:
0 22 * * * cd [inasafe-django directory]/deployment && make dbbackup
```

sftpbackup container will generate backups according to tower of hanoi scheme. 
For more information about what are the options provided by this containers, 
please go to [SFTP Backup Github Repo](https://github.com/kartoza/docker-sftp-backup/). 
To put it simply, if we give an option DAILY=3, MONTHLY=2, YEARLY=1, this 
container will leave 3 most recent daily backups, 2 most recent monthly backups, 
and 1 most recent yearly backup. These options specify the frequency of backups.

Additionally, if you have an SFTP server for storing these backups, it can 
also be configured to push these backups to that server. You need to provide 
sftp credentials for that. See [docker-compose.yml](docker-compose.yml) file 
to know that sftp_pg_credential.env and sftp_media_credential.env were included 
in the docker-compose configuration. You can either edit the file directly using 
a given template in [sftp_credential.env.template](sftp_credential.env.template) 
file, or using `all.yml` file to configure it using ansible.

In some occasion, you want to push all backups to your sftp server manually. 
You can execute this command:

```
make pushbackup
```

Or, you might want to receive all stored backup from sftp server, for example 
if you just changed your production server:

```
make pullbackup
```

If you have ssh access to your own live server, you could also fetch backups 
or media from it. Put the name of the server in your ssh config in TARGET_SERVER 
argument

```
make dbsync TARGET_SERVER=production-server
make mediasync TARGET_SERVER=production-server
```
