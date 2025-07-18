#!/bin/bash

APP_NAME="umemployedcelery"
RESOURCE_GROUP="UmEmployed_RG"

# Loop through .env lines, skipping comments and empty lines
cat .env | grep -v '^#' | grep -v '^$' | while IFS= read -r line; do
  KEY=$(echo "$line" | cut -d '=' -f1)
  VALUE=$(echo "$line" | cut -d '=' -f2-)
  echo "Setting $KEY..."
  az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings "$KEY=$VALUE" > /dev/null
done

echo "✅ Environment variables uploaded successfully!"
