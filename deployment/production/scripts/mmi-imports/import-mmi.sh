#!/usr/bin/env bash

# import contours sql table to database
su - postgres -c "psql gis < /backups/contours.sql"
su - postgres -c "psql gis < /backups/move-mmi.sql"
