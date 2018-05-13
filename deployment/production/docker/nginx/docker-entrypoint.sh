#!/usr/bin/env bash

# Clean up sites-enabled
echo "Clean sites-enabled"
rm -rf /etc/nginx/conf.d/*.conf
mkdir -p /etc/nginx/conf.d

if [ -z "${SSL}" ]; then
	echo "No SSL Configuration"
	export SSL_SUFFIX=""
else
	echo "Use SSL"
	export SSL_SUFFIX="-ssl"
fi

if [ -z "${SOURCE_PORT}" ]; then
	export SOURCE_PORT=8080
fi

if [ -z "${TARGET_PORT}" ]; then
	export TARGET_PORT=8080
fi

if [ -z "${SERVER_NAME}" ]; then
	export SERVER_NAME=*
fi

ENV_LIST='${SOURCE_PORT},${TARGET_PORT},${SERVER_NAME},${CERT_LOCATION},${CERT_KEY_LOCATION}'

if [ $# -eq 1 ]; then
	case $1 in
		# Debug mode, enable django.conf
		[Dd][Ee][Bb][Uu][Gg])
			echo "Run in debug mode"
			CONF_FILE=django${SSL_SUFFIX}.conf
			envsubst $ENV_LIST < /etc/nginx/sites-available/$CONF_FILE > /etc/nginx/conf.d/$CONF_FILE
			exec nginx -g "daemon off;"
			;;
		# Production mode, run using uwsgi
		[Pp][Rr][Oo][Dd])
			echo "Run in prod mode"
			CONF_FILE=uwsgi${SSL_SUFFIX}.conf
			envsubst $ENV_LIST < /etc/nginx/sites-available/$CONF_FILE > /etc/nginx/conf.d/$CONF_FILE
			exec nginx -g "daemon off;"
			;;
	esac
fi

# Run as bash entrypoint
exec $@
