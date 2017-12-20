#!/usr/bin/env bash

# Clean up sites-enabled
echo "Clean sites-enabled"
rm -rf /etc/nginx/conf.d/*.conf
mkdir -p /etc/nginx/conf.d

if [ $# -eq 1 ]; then
	case $1 in
		# Debug mode, enable django.conf
		[Dd][Ee][Bb][Uu][Gg])
			echo "Run in debug mode"
			CONF_FILE=django.conf
			ln -s /etc/nginx/sites-available/$CONF_FILE /etc/nginx/conf.d/$CONF_FILE
			exec nginx -g "daemon off;"
			;;
		# Production mode, run using uwsgi
		[Pp][Rr][Oo][Dd])
			echo "Run in prod mode"
			CONF_FILE=uwsgi.conf
			ln -s /etc/nginx/sites-available/$CONF_FILE /etc/nginx/conf.d/$CONF_FILE
			exec nginx -g "daemon off;"
			;;
	esac
fi

# Run as bash entrypoint
exec $@
