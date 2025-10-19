#!/bin/bash
set -e

# --- Configuration ---
PROJECT_ID="ninth-potion-455712-g9"
ENV_FILE=".env"

# Maps ENV_VAR_NAME to SECRET_NAME in Google Cloud
SECRETS_MAP=(
  "SUPABASE_URL/supabase-url"
  "SUPABASE_KEY/supabase-key"
)

# --- Script Body (No changes needed below) ---
echo "🔐 Storing Streamlit secrets in Google Secret Manager..."
# ... (The rest of the script is identical to the one from the guide) ...
if [ ! -f "$ENV_FILE" ]; then echo "❌ Error: $ENV_FILE not found!"; exit 1; fi
for mapping in "${SECRETS_MAP[@]}"; do
  ENV_VAR_NAME="${mapping%%/*}"; SECRET_NAME="${mapping##*/}"
  VALUE=$(grep -v '^#' "$ENV_FILE" | grep "$ENV_VAR_NAME" | cut -d '=' -f2-)
  if [ -z "$VALUE" ]; then echo "⚠️ Warning: '$ENV_VAR_NAME' not found. Skipping."; continue; fi
  echo "Storing '$ENV_VAR_NAME' as secret '$SECRET_NAME'..."
  if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
    gcloud secrets create "$SECRET_NAME" --replication-policy="automatic" --project="$PROJECT_ID"
  fi
  echo -n "$VALUE" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT_ID"
  echo "  -> ✅ Success."
done
echo "--------------------------------------------------"
echo "All secrets have been stored successfully."