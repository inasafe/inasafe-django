FROM kartoza/pg-backup:9.3
MAINTAINER tim@kartoza.com

# Add cronjob overrides to customize backup time trigger
ADD backups-cron /etc/cron.d/backups-cron
ADD backups.sh /backups.sh
 
CMD ["/start.sh"]
