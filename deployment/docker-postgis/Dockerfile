#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM kartoza/postgis:9.3-2.1
MAINTAINER Tim Sutton<tim@kartoza.com>

# add entry to pg_hba.conf
RUN echo "host    all    all    192.168.0.0/16   md5" >> /etc/postgresql/9.3/main/pg_hba.conf

CMD /start-postgis.sh
