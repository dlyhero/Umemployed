#!/bin/bash

echo "🔍 Verifying all .env variables are present as GitHub secrets..."
echo

# Extract variables from .env (excluding commented lines and empty lines)
ENV_VARS=$(grep -E "^[A-Z_]+" .env | cut -d'=' -f1 | sort)

# Get GitHub secrets
GH_SECRETS=$(gh secret list --repo dlyhero/Umemployed | awk '{print $1}' | sort)

echo "📝 Environment variables from .env:"
echo "$ENV_VARS"
echo
echo "🔑 GitHub secrets:"
echo "$GH_SECRETS"
echo

echo "❌ Missing secrets (in .env but not in GitHub):"
MISSING=0
for var in $ENV_VARS; do
    if ! echo "$GH_SECRETS" | grep -q "^$var$"; then
        echo "  - $var"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -eq 0 ]; then
    echo "  ✅ All environment variables are present as GitHub secrets!"
else
    echo "  ⚠️  Found $MISSING missing secrets"
fi

echo
echo "ℹ️  Extra secrets (in GitHub but not in .env):"
EXTRA=0
for secret in $GH_SECRETS; do
    if ! echo "$ENV_VARS" | grep -q "^$secret$"; then
        # Skip known extra secrets that are not from .env
        if [[ ! "$secret" =~ ^(ACR_|AZURE_CREDENTIALS|AZUREAPPSERVICE_|DB_|DOCKER_|ENV_FILE_CONTENTS).*$ ]]; then
            echo "  - $secret"
            EXTRA=$((EXTRA + 1))
        fi
    fi
done

if [ $EXTRA -eq 0 ]; then
    echo "  ✅ No unexpected extra secrets found"
fi

echo
echo "🎯 Summary:"
echo "  📝 Total .env variables: $(echo "$ENV_VARS" | wc -l)"
echo "  🔑 Total GitHub secrets: $(echo "$GH_SECRETS" | wc -l)"
echo "  ❌ Missing: $MISSING"
echo "  ➕ Extra (non-.env): $EXTRA"
