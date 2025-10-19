#!/bin/bash
set -e

# --- Configuration ---
SERVICE_ACCOUNT_EMAIL="stark-vertex-ai@ninth-potion-455712-g9.iam.gserviceaccount.com"
PROJECT_ID="ninth-potion-455712-g9"

echo "🛡️ Granting GCS permissions to service account: $SERVICE_ACCOUNT_EMAIL"
echo "--------------------------------------------------"

# Grant permission to read and write to Google Cloud Storage
echo "1. Granting Storage Object Admin role (roles/storage.objectAdmin)..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"

echo "--------------------------------------------------"
echo "✅ GCS permissions granted successfully."