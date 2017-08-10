#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM kartoza/django-base
MAINTAINER Tim Sutton<tim@kartoza.com>

RUN apt-get update -y; apt-get -y --force-yes install yui-compressor

# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

ADD REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi

# Install Gettext
RUN apt-get update -y; apt-get install -y gettext

# Clone source code

ADD entry-point.sh /entry-point.sh

RUN mkdir -p /home/src/
RUN mkdir -p /home/web/
RUN cd /home/src
RUN git clone --branch v3.4 --depth 1 https://github.com/inasafe/inasafe-django.git

# Copy only django_project folder
RUN cp -r /home/src/django_project /home/web/

WORKDIR /home/web/django_project
CMD ["/entry-point.sh"]
