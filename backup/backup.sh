#!/bin/bash

# Backup script to dump Heroku Postgres database

# Define your Heroku app name
HEROKU_APP_NAME="umemployed-app"

# Get the DATABASE_URL from Heroku config
DATABASE_URL=$(heroku config:get DATABASE_URL --app $HEROKU_APP_NAME)

# Define the backup file name with a timestamp
BACKUP_FILE="db_backup_$(date +'%Y%m%d_%H%M%S').sql"

# Use pg_dump to create a backup of the database
pg_dump $DATABASE_URL -Fc -f $BACKUP_FILE

# Notify the user
echo "Database backup saved to $BACKUP_FILE"
