FROM nginx

ADD docker-entrypoint.sh /docker-entrypoint.sh
ADD conf/* /etc/nginx/sites-available/

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["prod"]
