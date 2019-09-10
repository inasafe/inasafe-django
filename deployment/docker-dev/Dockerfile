#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM kartoza/django-base
MAINTAINER Tim Sutton<tim@kartoza.com>

RUN apt-get update -y; apt-get -y --force-yes install yui-compressor

# This section taken on 2 July 2015 from
# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get update -y; apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
# Comment out PermitRootLogin setting, whatever it is
RUN sed -i 's/^PermitRootLogin */#PermitRootLogin /' /etc/ssh/sshd_config
# Write out PermitRootLogin setting at the end
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# End of cut & paste section


# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

ADD sitecustomize.py /usr/local/lib/python2.7/site-packages/sitecustomize.py
ADD REQUIREMENTS.txt /REQUIREMENTS.txt
ADD REQUIREMENTS-dev.txt /REQUIREMENTS-dev.txt
RUN pip install -r /REQUIREMENTS.txt
RUN pip install -r /REQUIREMENTS-dev.txt
ADD bashrc /root/.bashrc

# Install Gettext
RUN apt-get update -y; apt-get install -y gettext

# --------------------------------------------------------
# Open ports as needed
# --------------------------------------------------------

# Open port 8080 as we will be running our django dev server on
EXPOSE 8080
# Open port 22 as we will be using a remote interpreter from pycharm
EXPOSE 22
# Open port 8088 for celery worker debugging
EXPOSE 8088

CMD ["/usr/sbin/sshd", "-D"]
