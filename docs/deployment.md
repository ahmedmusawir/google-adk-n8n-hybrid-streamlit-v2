Of course. Here is the `deployment.md` for the Streamlit frontend, detailing the complete process we established.

---

### `/docs/deployment.md`

````markdown
# Streamlit Frontend Deployment Guide

This guide provides a step-by-step process for deploying the **Streamlit Frontend** application to Google Cloud Run. The process uses the "deploy from source" method, secure authentication via an IAM Service Account, and secret management with Google Secret Manager.

---

## Prerequisites

Before you begin, ensure you have the following:

1.  **Google Cloud SDK (`gcloud` CLI):** Installed and authenticated. Run `gcloud auth login` and `gcloud config set project [YOUR_PROJECT_ID]`.
2.  **Project Source Code:** The complete Streamlit project directory.
3.  **Local `.env` File:** Create a file named `.env` in the project root containing your Supabase credentials. This file is used by the secrets script and should **not** be committed to version control.

    **`.env` Template:**

    ```
    SUPABASE_URL=[https://your-project-ref.supabase.co](https://your-project-ref.supabase.co)
    SUPABASE_KEY=your-supabase-anon-key
    ```

---

## One-Time Setup

These steps are typically performed only once per project or when credentials change.

### Step 1: Grant Permissions

The service needs permission to read and write to Google Cloud Storage.

**Script: `grant_streamlit_permissions.sh`**

```bash
#!/bin/bash
set -e
SERVICE_ACCOUNT_EMAIL="stark-vertex-ai@ninth-potion-455712-g9.iam.gserviceaccount.com"
PROJECT_ID="ninth-potion-455712-g9"
echo "🛡️ Granting GCS permissions to service account: $SERVICE_ACCOUNT_EMAIL"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"
echo "✅ GCS permissions granted successfully."
```
````

**To Use:** Make the script executable (`chmod +x grant_streamlit_permissions.sh`) and run it once (`./grant_streamlit_permissions.sh`).

### Step 2: Store Secrets

This script reads your local `.env` file and securely stores the Supabase credentials in Google Secret Manager.

**Script: `store_streamlit_secrets.sh`**

```bash
#!/bin/bash
set -e
PROJECT_ID="ninth-potion-455712-g9"
ENV_FILE=".env"
SECRETS_MAP=(
  "SUPABASE_URL/supabase-url"
  "SUPABASE_KEY/supabase-key"
)
echo "🔐 Storing Streamlit secrets in Google Secret Manager..."
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
```

**To Use:** Run the script to initialize or update your cloud secrets (`./store_streamlit_secrets.sh`).

---

## Core Files for Deployment

### 1\. The Startup Command (`Procfile`)

This file gives Cloud Run the explicit command needed to start the Streamlit application.

**File Location:** `/[PROJECT_ROOT]/Procfile`

```
web: streamlit run chat.py --server.port $PORT --server.enableCORS false
```

### 2\. The Ignore File (`.gcloudignore`)

This file is critical. It prevents local development files from being uploaded and includes an exception to ensure `config.json` is deployed.

**File Location:** `/[PROJECT_ROOT]/.gcloudignore`

```
# Ignore the virtual environment
.venv/

# Ignore Python cache files
__pycache__/
*.pyc

# Ignore Git directory and local environment files
.git/
.gitignore
.env

# Ignore any local log files or sensitive keys
*.log
*.json

# BUT, make an exception and DO include our app's config file
!config.json
```

---

## The Deployment Script (`deploy.sh`)

This script automates the final deployment to Cloud Run.

```bash
#!/bin/bash
set -e

# --- Configuration ---
SERVICE_NAME="adk-streamlit-frontend-v2"
REGION="us-east1"
PROJECT_ID="ninth-potion-455712-g9"
SERVICE_ACCOUNT_EMAIL="stark-vertex-ai@${PROJECT_ID}.iam.gserviceaccount.com"
WRAPPER_URL="[https://adk-wrapper-prod-v2-952978338090.us-east1.run.app](https://adk-wrapper-prod-v2-952978338090.us-east1.run.app)"

# --- Deployment ---
echo "🚀 Deploying service: $SERVICE_NAME"
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --allow-unauthenticated \
  --service-account="$SERVICE_ACCOUNT_EMAIL" \
  --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest" \
  --set-env-vars="APP_ENV=cloud,WRAPPER_URL=${WRAPPER_URL}"

echo "--------------------------------------------------"
echo "✅ Deployment complete!"
echo "📡 Service URL:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)"
```
