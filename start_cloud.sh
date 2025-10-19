#!/bin/bash
set -e

echo "🚀 Starting Streamlit Frontend in 'cloud' mode..."
echo "   Targeting the live ADK Wrapper on Cloud Run."
echo "--------------------------------------------------"

# Set the environment variable to 'cloud' and run Streamlit
APP_ENV="cloud" streamlit run ./chat.py --logger.level error