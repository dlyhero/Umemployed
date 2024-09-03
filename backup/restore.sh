#!/bin/bash

# Restore script to upload database to Heroku Postgres

# Define your Heroku app name
HEROKU_APP_NAME="umemployed-app"

# Get the DATABASE_URL from Heroku config
DATABASE_URL=$(heroku config:get DATABASE_URL --app $HEROKU_APP_NAME)

# Extract database components
DB_HOST=$(echo $DATABASE_URL | sed -e 's/.*@//' -e 's/:.*//')
DB_PORT=$(echo $DATABASE_URL | sed -e 's/.*://' -e 's/\/.*//')
DB_NAME=$(echo $DATABASE_URL | sed -e 's/.*\///')
DB_USER=$(echo $DATABASE_URL | sed -e 's/.*:\/\///' -e 's/:.*//')

# Define the backup file to restore from
BACKUP_FILE="$1"

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
  echo "Please provide the backup file to restore from."
  exit 1
fi

# Restore the backup
pg_restore --verbose --clean --no-acl --no-owner -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME $BACKUP_FILE

# Notify the user
echo "Database restored from $BACKUP_FILE"
