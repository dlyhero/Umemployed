#!/bin/bash

# Restore script to upload database to Heroku Postgres

# Define your Heroku app name
HEROKU_APP_NAME="umemployed-app"

# Get the DATABASE_URL from Heroku config
DATABASE_URL=$(heroku config:get DATABASE_URL --app $HEROKU_APP_NAME)

# Define the backup file to restore from
# Replace with the exact filename or pass as an argument
BACKUP_FILE="$1"

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
  echo "Please provide the backup file to restore from."
  exit 1
fi

# Use pg_restore to restore the database from the backup file
pg_restore --verbose --clean --no-acl --no-owner -h $(echo $DATABASE_URL | cut -d'/' -f3 | cut -d':' -f1) -U $(echo $DATABASE_URL | cut -d':' -f2 | cut -d'/' -f3 | cut -d'@' -f1) -d $(echo $DATABASE_URL | cut -d'/' -f4) $BACKUP_FILE

# Notify the user
echo "Database restored from $BACKUP_FILE"
