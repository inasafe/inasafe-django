# Prerequisite and Requirement

In order to deploy this service, you need to perform these instructions:


# NFS Shared Storage Setup

You need to have one machine as a central shared storage. This machine will act 
as a central access and management to a persistent data.

## Installation

1. Choose a machine. 

It **should** only be able to be accessed from a an inside or private network. 
Depending on your organization policies you should set up a firewall or perform 
other security measures so this machine is secured from the internet.

We will assume you are using Ubuntu/Debian Linux to illustrate NFS installation.

2. Install NFS Server

We are using this article for a reference [Rancher Storage Service - NFS](http://rancher.com/docs/rancher/v1.6/en/rancher-services/storage-service/rancher-nfs/)

Install on Ubuntu LTS 16.04:

```
sudo apt update
sudo apt install nfs-kernel-server
```

3. Configure shared directory

On this machine, you need to decide where to put your export directory, that is 
a directory that will be shared (`/home/nfs` in this example)

```
sudo mkdir -p /home/nfs
```

For a very specific reasons, we need to have root to own this directory. 
Because this dir will be accessed by containers. This will avoid permission issues.

```
sudo chown root:root /home/nfs
```

4. Configure exporting options

You need to specify how this dir will be shared. Again, for a very specific reason,
we need to add `no_root_squash` for mount options.

Modify `/etc/exports` config file then add this line:

Open file `/etc/exports`

```
nano /etc/exports
```

Add this line:

```
/home/nfs	*(rw,sync,no_subtree_check,no_root_squash)
```

Note that you can specify a whitelist by replacing `*` with a subnet of whitelisted 
machine. But it is probably just easier if you set up firewall in the first place.

5. Apply changes, restart NFS Server

```
sudo systemctl restart nfs-kernel-server
```

6. Perform mount test

Mount the directory from other machine (that can access NFS Server)
to see that it works. For example, do this from a different machine:

```
sudo mkdir -p /mnt/nfs-mount
mount -t nfs [nfs-server-address]:/home/nfs /mnt/nfs-mount
```

Try creating/touching a file from NFS Server and see if it can be seen on client.

After you done testing and making sure that it works, don't forget to perform umount:

```
umount /mnt/nfs-mount
```

If you failed to see/modify the shared file, make sure the server can be accessed 
from client.


# Configure Inotify Limit

InaSAFE Processor heavily uses inotify to watch shakemaps directory. To avoid 
the services hits Inotify Limit, perform necessary configuration:

Reference [Increasing Inotify Limit](https://github.com/guard/listen/wiki/Increasing-the-amount-of-inotify-watchers)

1. View the current limit

The variable we're interested with is `fs.inotify.max_user_watches` and `fs.inotify.max_user_instances`

```
sudo sysctl fs.inotify.max_user_watches
```

It will return 8192 in default Ubuntu. 

2. Increase this size to a big number.
 
Open `/etc/sysctl.conf` and add these lines:

```
fs.inotify.max_user_watches=163840
fs.inotify.max_user_instances=512
```

Increase max_user_watches if somehow the server hit the limit again.

3. Reload `sysctl`

```
sudo sysctl -p
```

# Rancher Server

Install Rancher server on a machine that will become the manager.

1. Requirements

Make sure your machine meets this requirement:
[Requirements](http://rancher.com/docs/rancher/v1.6/en/installing-rancher/installing-server/#requirements)

Summary:
- A Linux host
- Docker engine installed. [Installing docker engine CE](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository)
- 1 GB RAM minimum
- MySQL server (if using a physical machine)
- Location for storing MySQL db data (if using bind mount to host volume)

2. Follow installation path that meets your requirement

Installation documentation listed here: [Installing Rancher](http://rancher.com/docs/rancher/v1.6/en/installing-rancher/installing-server/#requirements)
Either you are using physical MySQL server or bind mount, make sure your data 
is persisted somewhere so it doesn't get lost. Use `stable` tag for production.

Sample to use bind mount:

Make sure your location to store MySQL data exists:

```
mkdir -p /home/rancher-data
```

Launch rancher with bind mount to store data:
[LAUNCHING RANCHER SERVER - SINGLE CONTAINER - BIND MOUNT MYSQL VOLUME](http://rancher.com/docs/rancher/v1.6/en/installing-rancher/installing-server/#launching-rancher-server---single-container---bind-mount-mysql-volume)

We mount `/home/rancher`

```
sudo docker run -d -v /home/rancher-data:/var/lib/mysql --restart=unless-stopped -p 8080:8080 rancher/server:stable
```

3. Open Rancher UI

After you finished installing Rancher, access it through the web UI. For example 
by default it was exposed to port 8080:

http://rancher-server:8080/

4. Configure Access Control

[Reference](http://rancher.com/docs/rancher/v1.6/en/configuration/access-control/#access-control)

Follow the instruction to decide an account type.

5. Create Environment

Create a new Environment for managing InaSAFE Processor. Perform these series 
of instructions:

Edit environment variable for `Cattle`, we are going to use NFS driver for this template.

In the **Storage** section, find **Rancher NFS** and click Enable.

Choose latest version.

Configure options for `NFS Server` and `Export Base Directory` (`/home/nfs`). 
Fill in with information of NFS Server you setup previously.

Click Configure when you're done.

Now, you can create a new Environment. Put a human friendly name, for example 
**InaSAFE Realtime**.

Switch to that Environment by clicking it on the dashboard.


After this is completed, you are now ready to add Rancher Agents

# Rancher Agents

Install docker engine on this machine:

Refer the instruction to install docker:

[Install Docker Engine CE](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository)

Install docker engine on a machine that will be used as agents.

Configure Inotify Limit again for this agent [Configure Inotify Limit](#configure-inotify-limit)

You can add one or more Agents as you needed, but it is sufficient to have 
just one powerful agent for InaSAFE Realtime.

From the dashboard, go to Infrastructure > Hosts > Add Host

You will be redirected to an instruction page, follow the instruction.

You can optionally add **label** to this host. Label is a way for user to easily 
identify and categorize machines. For example, you might want to add `High performance` 
**label** for a very powerful machine to run InaSAFE analysis. This is useful when 
you want to configure a constraint to specify where a service should be run (optionally later).

Specify the public IP of the machine, that is an IP that this Rancher Server can access 
to communicate with the agent.

This Rancher Agent machine needs to be able to access NFS Server. 
Test it by doing mount test on this machine.

Just follow the instruction and the agent will be detected automatically by Rancher 
Server.

Set up more Agents if you need.

If you succeed, a new hosts box can be seen in Infrastructure > Hosts page.
You can also see the spec, like the hardware and docker engine version.
