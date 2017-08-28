# InaSAFE Django

This repo and folder are specifically used to explain the orchestration of 
InaSAFE Django.

# What is InaSAFE Django

InaSAFE Django is a django web app provided as a user interface for InaSAFE Realtime.
There are 3 tabs specifically provided:

- Shakemaps
- Flood
- Ash

Each one is a specific for InaSAFE Realtime hazard type. All of these service 
are specific and custom tailored needs of InaSAFE Realtime for Indonesian Hazards.

# The Architecture

InaSAFE Processor orchestration relies on docker containers and will be managed 
by a Rancher server instance. This will allow sysadmin to easily manage container 
services, data, and scale if necessary. Listed below are some different terminologies 
that need to be understand by a sysadmin to maintain this service:

- Basic Understanding of NFS Shared Storage Service
- Docker containers and micro service architecture
- Rancher server and agents as docker containers managers
- General data management and backups

## NFS Shared Storage Service

InaSAFE Processor needs to store/persist hazard data given by each data source.
It also needs to store exposure data and analysis result. The easiest way to make 
these data available to each services and persist/replicate it easily is using 
a Shared Storage Service. With a shared storage service, sysadmin can have 
a central location as a main data bank. We propose a dedicated NFS Server to 
store all these data (with big storage) in central location. This NFS Server 
then can be accessed by docker containers, but should not be able to be accessed 
from outside network (internet). Sysadmin can then manage data like creating backup 
or snapshot from a central location.

In addition for having a Shared Storage Service, we also propose to use a 
replication service like BitTorrent Sync to easily setup new instance of 
InaSAFE Processor if needed (like migrations or moving to a new machine). 
BtSync will make it easier for sysadmin to migrate data. With BtSync, all you 
have to do is share the appropriate key (Read only or Read Write) to a replication 
container service. This key can also be used to replicate the data to your other
desired machine (local machine or server)

## Docker containers and Micro Service Architecture

We heavily use Docker to make it easy for sysadmin to deploy services. Docker 
is a tool to create/run a distributed application, see: [Docker](https://www.docker.com).
With docker, we can easily build and run service on any Linux platform (or even mac and windows).
This enabled the developer to easily create a service application and sysadmin 
can easily run the application on server machine.

Docker packaged its application as a small lightweight virtual machine called containers.
Sysadmin can run containers and Developers build them. When containers were made 
to perform one specific tasks, we called this services. An orchestration defined 
one or more different services to perform a series of tasks together and specify 
how they communicate with each other. This is called Micro Service Architecture. 
When we talk about a Docker orchestration, we specify how services work together, 
how they communicate with each other, how they can be started and stopped, etc.

The orchestration of docker containers were described using a file called 
`docker-compose.yml`. We can see services definition in `docker-compose.yml` file. 
A group of containers specified by a `docker-compose.yml` file is often called as 
a `stack`.
  
## Rancher Server and Agents

It is possible to deploy or manage docker containers or stacks using command 
line tools. But this process needs a learning curve and perhaps undesirable for 
new sysadmin not familiar with Docker. To ease the process, we use Rancher as 
container/stack management tools, see [Rancher](http://rancher.com). 
Rancher uses Graphical User Interface via Web Application so it is easy to use 
and understand. Rancher made it possible for 
sysadmin to just focus on deployment and management without having to know too 
much details about Docker.
  
Rancher have two specific part, Rancher Server and Agents. A Rancher Server 
is the manager that provides the Graphical User Interface. We can easily deploy 
Rancher Server because it is too, a docker container/service. You can view the 
Web UI just by deploying Rancher Server, however it needs one (or more) Rancher 
Agents to actually run service containers. You can install Rancher Agents on 
machine that will do the actual work (providing the services you want to deploy), 
and have those machines registered to a Rancher Server so it can be managed.

To easily familiarize yourself with Rancher, you need to understand several 
terminologies:

- Rancher Server: A machine installed with Rancher Server will manage deployment.
  This machine will need to be exposed for a group people to use.
- Rancher Agents: one or several machines installed with rancher agents will act
  as a resource for Rancher Server to use to deploy docker containers. This agents
  can be any machine (preferably Linux) with docker installed with sufficient 
  hardware requirements depending on what kind of service you want to deploy.
- Environment: Term used by Rancher to categorize container deployment setting. 
  You might want to create an Environment for a group of Stacks that will perform 
  as one big services.
- Stack: A group of containers (micro services) defined by docker-compose.yml 
  to perform a certain task or provides services.
- Infrastructure Stack: Special stack used internally by Rancher
- Catalog: Template provided by Rancher and/or Community that can be used as a
  stack by sysadmin. Usually contains a very specific functionality for Sysadmin. 
  Like a storage Catalog or monitoring service.

# Prerequisite

Specific prerequisite document can be seen here [Prerequisite](PREREQUISITE.md)

After you finished your prerequisite set up, continue to deploy the services.
Service can be deployed using rancher workflow. A sample docker-compose file is created
in [docker directory](deployment/production/docker/docker-compose.yml)
