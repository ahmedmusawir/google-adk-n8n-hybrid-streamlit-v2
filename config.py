# config.py (for Streamlit app)
import json
import os
import logging
from typing import Dict, List

def load_settings():
    """
    Loads configuration from config.json based on the APP_ENV environment variable.
    """
    env = os.getenv("APP_ENV", "local")
    
    try:
        with open("config.json", "r") as f:
            config_data = json.load(f)
    except Exception as e:
        logging.error(f"Could not load or parse 'config.json': {e}")
        return None, None, []

    env_settings = config_data.get("environments", {}).get(env, {})
    wrapper_url = env_settings.get("wrapper_url")
    adk_bundle_url = env_settings.get("adk_bundle_url")
    agents = config_data.get("agents", [])
    
    return wrapper_url, adk_bundle_url, agents

WRAPPER_URL, ADK_BUNDLE_URL, AGENT_OPTIONS = load_settings()