#!/bin/bash
set -e

# --- Configuration ---
SERVICE_NAME="adk-streamlit-frontend-v2"
REGION="us-east1"
PROJECT_ID="ninth-potion-455712-g9"
SERVICE_ACCOUNT_EMAIL="stark-vertex-ai@${PROJECT_ID}.iam.gserviceaccount.com"
WRAPPER_URL="https://adk-wrapper-prod-v2-952978338090.us-east1.run.app"

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