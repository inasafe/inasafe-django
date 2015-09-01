#!/bin/sh
if [ $# -ne 2 ]
then 
	echo 'How to user:'
	echo 'setup-apt-cache.sh [interface_name] [foldername]'
fi

IP_ADDRESS=$(/sbin/ifconfig $1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')

echo "IP address : $IP_ADDRESS"

echo "Acquire::http { Proxy \"http://$IP_ADDRESS:3142\"; };" > "$2/71-apt-cacher-ng"
