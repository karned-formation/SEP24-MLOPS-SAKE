#!/bin/sh
set -e  # Exit immediately if a command exits with a non-zero status

# Load secrets if they exist
if [ -f /run/secrets/secrets ]; then
    export $(cat /run/secrets/secrets | xargs)
fi

# Activate virtual environment
. /app/SEP24-MLOPS-SAKE/.venv/bin/activate

# Authenticate with DagsHub and pull DVC data
dagshub login --token "$DAGSHUB_TOKEN"
dvc remote modify origin --local access_key_id "$DAGSHUB_ACCESS_KEY_ID"
dvc remote modify origin --local secret_access_key "$DAGSHUB_SECRET_ACCESS_KEY"
dvc pull --force || true


# Execute the given command (uvicorn)
exec "$@"
